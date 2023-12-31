import re

from django.template import Library, Node, TemplateSyntaxError
from django.utils.translation import gettext as _
from django.core.cache import cache
from django.conf import settings

from src.core import paper_forms
from src.core.models import Submission, AdvancedSettings, EthicsCommission
from src.docstash.models import DocStash


register = Library()

register.filter('type_name', lambda obj: type(obj).__name__)
register.filter('endswith', lambda obj, end: obj.endswith(end))
register.filter('not', lambda obj: not obj)
register.filter('multiply', lambda a, b: a * b)
register.filter('euro', lambda val: ("€ %.2f" % float(val)).replace('.', ','))
register.filter('is_none', lambda obj: obj is None)

@register.filter
def getitem(obj, name):
    try:
        return obj[name]
    except KeyError:
        return None

@register.filter
def ec_number(submission):
    if submission:
        return submission.get_ec_number_display()
    return None

@register.filter
def get_field_info(formfield):
    if formfield and hasattr(formfield.form, '_meta'):
        return paper_forms.get_field_info(model=formfield.form._meta.model, name=formfield.name)
    else:
        return None

@register.filter
def form_value(form, fieldname):
    if form.data:
        return form._raw_value(fieldname)
    try:
        return form.initial[fieldname]
    except KeyError:
        return None
        
@register.filter
def simple_timedelta_format(td):
    if not td.seconds:
        return "0"
    minutes, seconds = divmod(td.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    result = []
    if hours:
        result.append("%sh" % hours)
    if minutes:
        result.append("%smin" % minutes)
    if seconds:
        result.append("%ss" % seconds)
    return " ".join(result)
    
@register.filter
def smart_truncate(s, n):
    if not s:
        return ""
    if len(s) <= n:
        return s
    return "%s …" % re.match(r'(.{,%s})\b' % (n - 2), s).group(0)
    

@register.filter
def has_submissions(user):
    return (
        Submission.unfiltered.mine(user).exists() or
        DocStash.objects.filter(
            group='src.core.views.submissions.create_submission_form',
            owner=user, current_version__gte=0
        ).exists()
    )

@register.filter
def has_assigned_submissions(user):
    return Submission.objects.reviewed_by_user(user).exists()

@register.filter
def is_docstash(obj):
    return isinstance(obj, DocStash)

@register.filter
def yes_no_unknown(v):
    if v is True:
        return _('yes')
    elif v is False:
        return _('no')
    else:
        return _('Unknown')

@register.filter
def last_recessed_vote(top):
    if top.submission:
        return top.submission.get_last_recessed_vote(top)
    return None


@register.filter
def allows_amendments_by(sf, user):
    return sf.allows_amendments(user)
    
@register.filter
def allows_edits_by(sf, user):
    return sf.allows_edits(user)


class BreadcrumbsNode(Node):
    def __init__(self, varname):
        super().__init__()
        self.varname = varname

    def render(self, context):
        user = context['request'].user
        if not user.is_anonymous():
            crumbs_cache_key = 'submission_breadcrumbs-user_{0}'.format(user.pk)
            crumb_pks = cache.get(crumbs_cache_key, [])
            crumbs = list(Submission.objects.filter(pk__in=crumb_pks).only('ec_number'))
            crumbs.sort(key=lambda x: crumb_pks.index(x.pk))
            context[self.varname] = crumbs
        return ''

@register.tag
def get_breadcrumbs(parser, token):
    try:
        name, as_, varname = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError('{% get_breadcrumbs as VAR %} expected')
    return BreadcrumbsNode(varname)


# class DbSettingNode(Node):
#     def __init__(self, name, varname):
#         super().__init__()
#         self.name = name
#         self.varname = varname

#     def render(self, context):
#         name = self.name.resolve(context)
#         val = AdvancedSettings.objects.values_list(name, flat=True)[0]

#         if self.varname:
#             context[self.varname] = val
#             return ''
#         else:
#             return val
class DbSettingNode(Node):
    def __init__(self, name, varname):
        super().__init__()
        self.name = name
        self.varname = varname

    def render(self, context):
        name = self.name.resolve(context)
        values_list = AdvancedSettings.objects.values_list(name, flat=True)

        if values_list:
            val = values_list[0]

            if self.varname:
                context[self.varname] = val
                return ''
            else:
                return val
        else:
            # Handle the case when values_list is empty
            return ''  # You might want to return some default value or handle it differently


@register.tag
def db_setting(parser, token):
    bits = token.split_contents()
    if len(bits) == 2:
        kw_, name = bits
        varname = None
    elif len(bits) == 4 and bits[2] == 'as':
        kw_, name, as_, varname = bits
    else:
        raise TemplateSyntaxError('{% db_setting name [as VAR] %}')

    name = parser.compile_filter(name)
    return DbSettingNode(name, varname)


@register.simple_tag
def ec_name():
    ec = EthicsCommission.objects.get(uuid=settings.ETHICS_COMMISSION_UUID)
    return ec.name
