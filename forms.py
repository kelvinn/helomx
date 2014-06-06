from django import forms
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from helomx import events
from helomx.hosts.models import Mailserver, MailserverPrefs
from helomx.profiles.models import Company, Engineer
from helomx.mxhelpers import get_rbl_list
from helomx.contact.models import Contact
from helomx.billing.models import InvoiceHistory
from helomx.infolog.models import Ticket

TICKET_TYPE = (
    ('freecredit', 'Free Credit Request'),
    ('request', 'Feature Request'),
    ('complaint', 'Complaint'),
    ('problem', 'Technical Problem'),
    ('billing', 'Billing Issue'),
    ('comment', 'General Comment'),
)

CONTACT_METHOD = (
    ('phone', 'By Phone'),
    ('email', 'Via Email'),
    ('inperson', 'In Person'),
    ('none', 'No Response Needed'),
)

BILLING_AMOUNT = (
    ('10', '$10 USD'),
    ('25', '$25 USD'),
    ('50', '$50 USD'),
    ('100', '$100 USD'),
    ('500', '$500 USD'),
)

attrs_dict = { 'class': 'norm_required' }
textbox_dict = { 'class': 'text_required' }
tag_dict = { 'class': 'tag_required' }


class BillingForm(forms.Form):
    credit_added = forms.CharField(widget=forms.Select(choices=BILLING_AMOUNT), max_length=7, label='Desired Credit Amount')

class EngineerProfileForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs=attrs_dict), max_length=75, label='First Name')
    last_name = forms.CharField(widget=forms.TextInput(attrs=attrs_dict), max_length=75, label='Last Name')
    timezone = forms.CharField(widget=forms.Select(choices=events.timezones(), attrs=attrs_dict), max_length=200, label='Timezone')
    email = forms.CharField(widget=forms.TextInput(attrs=attrs_dict), max_length=64, label='Email')
    mobile = forms.CharField(widget=forms.TextInput(attrs=attrs_dict), max_length=64, label='Mobile')

class EngineerPermForm(forms.Form):
    can_edit_mx = forms.BooleanField(required=False, label='Can Edit Mailservers')
    can_edit_engineers = forms.BooleanField(required=False, label='Can Edit Engineer')
    
class AddEngineerForm(forms.Form):
    user = forms.CharField(widget=forms.TextInput(attrs=attrs_dict), max_length=75, label='Username')
    first_name = forms.CharField(widget=forms.TextInput(attrs=attrs_dict), max_length=75, label='First Name')
    last_name = forms.CharField(widget=forms.TextInput(attrs=attrs_dict), max_length=75, label='Last Name')
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict),
                                label=u'Password')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict),
                                label=u'Password (verify)')
    timezone = forms.CharField(widget=forms.Select(choices=events.timezones(), attrs=attrs_dict), max_length=200, label='Timezone')
    email = forms.CharField(widget=forms.TextInput(attrs=attrs_dict), max_length=64, label='Email')
    mobile = forms.CharField(widget=forms.TextInput(attrs=attrs_dict), max_length=64, label='Mobile (Optional)', required=False)
    can_edit_mx = forms.BooleanField(required=False, label='Can Edit Mailservers')
    can_edit_company = forms.BooleanField(required=False, label='Can Edit Company')
    can_edit_billing = forms.BooleanField(required=False, label='Can Edit Billing')
    
    def clean_user(self):
        if self.cleaned_data.get('user'):
            value = self.cleaned_data['user']
            try:
                user_name = User.objects.get(username=slugify(value))
                if user_name:
                    raise forms.ValidationError("This username has already been used, please pick a new one.")
            except User.DoesNotExist:
                return value

    def clean_email(self):
        value = self.cleaned_data.get('email')
        try:
            user_list = User.objects.filter(email=value)
            if user_list.count() == 0:
                return value
            else:
                raise forms.ValidationError("This email has already been used.")
        except User.DoesNotExist:
            raise forms.ValidationError("This email has already been used.")

class DiagnosticForm(forms.Form):
    domain = forms.CharField(widget=forms.TextInput(attrs=attrs_dict), max_length=75, label='Domain Name')

    def clean_domain(self):
        if self.cleaned_data.get('domain'):
            import dns.resolver
            value = self.cleaned_data['domain']
            try:
                dns.resolver.query(value, 'MX')
                return value

            except:
                raise forms.ValidationError("The domain you entered is invalid.")


class MailserverForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs=attrs_dict), max_length=50, label="Client's Name")
    mx_url = forms.CharField(widget=forms.TextInput(attrs=attrs_dict), max_length=75, label='Domain Name (URL)')
    ipaddr = forms.CharField(widget=forms.TextInput(attrs=attrs_dict), max_length=75, label='IP Address')
    #rbl = forms.MultipleChoiceField(choices=get_rbl_list(), widget=forms.CheckboxSelectMultiple(), required=False)

    def clean_name(self):
        if self.cleaned_data.get('name'):
            value = self.cleaned_data['name']
            try:
                mailserver = Mailserver.objects.get(name=value)
                if mailserver:
                    raise forms.ValidationError("This name has already been used, please pick a new one.")
            except Mailserver.DoesNotExist:
                return value

class ChangePWForm(forms.Form):
    """
    Form for changing a password.

    Validates that the password is entered twice and matches,

    """
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict),
                                label=u'New Password')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict),
                                label=u'New Password (verify)')

    def clean_password2(self):
        """
        Validates that the two password inputs match.

        """
        if self.cleaned_data.get('password1', None) and self.cleaned_data.get('password2', None) and \
           self.cleaned_data['password1'] == self.cleaned_data['password2']:
            return self.cleaned_data['password2']
        raise forms.ValidationError(u'You must type the same password each time')


class UptMailserverForm(forms.ModelForm):
    def __init__(self, mx, *args, **kwargs):
        super(UptMailserverForm, self).__init__(*args, **kwargs)
        self.mx_obj = mx
        self.fields['alert_contact'].queryset = Engineer.objects.filter(company=mx.company)

    class Meta:
        model=Mailserver
        exclude = ('company', 'slug', 'rbl', 'webmail_url', 'active', 'port_status', 'blacklist_status', 'note', 'is_active')

class MailserverPrefsForm(forms.ModelForm):
        
    class Meta:
        model=MailserverPrefs
        exclude = ('mailserver')

class TicketForm(forms.Form):
    ticket_type = forms.CharField(widget=forms.Select(choices=TICKET_TYPE), max_length=20, label='What type of request is this?')
    contact_method = forms.CharField(widget=forms.Select(choices=CONTACT_METHOD), max_length=20, label='How would you like us to contact you?')
    content = forms.CharField(widget=forms.Textarea(attrs=textbox_dict), label='Ticket Contents')

    class Meta:
        model=Ticket
        exclude = ('ticket_id', 'created_by', 'add_time', 'close_time',
                        'status', 'note')

class CompanyForm(forms.ModelForm):
        
    class Meta:
        model=Company
        exclude = ('primary_contact', 'slug')

class UserForm(forms.ModelForm):
    
    class Meta:
        model=User
        exclude = ('username', 'password', 'is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined', 'groups', 'user_permissions')

    def clean_email(self):
        value = self.cleaned_data.get('email')
        try:
            user_list = User.objects.filter(email=value)
            if user_list.count() == 0:
                return value
            else:
                if self.email == value:
                    return value
                else:
                    raise forms.ValidationError("This email has already been used.")
        except:
            raise forms.ValidationError("This email has already been used.")

class UpdateNameForm(forms.ModelForm):

    class Meta:
        model=User
        exclude = ('username', 'password', 'email', 'is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined', 'groups', 'user_permissions')

class EngineerForm(forms.ModelForm):
    
    class Meta:
        model=Engineer
        exclude = ('user', 'company')

class ContactForm(forms.ModelForm):

    class Meta:
        model=Contact
        exclude = ('response', 'responded')

class AddCompanyForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs=attrs_dict), max_length=75, label='Company Name<span class="red">*</span>')
    postcode = forms.CharField(widget=forms.TextInput(attrs=attrs_dict), max_length=12, label='Postcode (Optional)', required=False)
    city = forms.CharField(widget=forms.TextInput(attrs=attrs_dict), max_length=25, label='City (Optional)', required=False)
    street = forms.CharField(widget=forms.Textarea(), max_length=40, label='Street (Optional)', required=False)
    state = forms.CharField(widget=forms.TextInput(attrs=attrs_dict), max_length=35, label='State (Optional)', required=False)
    country = forms.CharField(widget=forms.Select(choices=[('0', '')]+events.country_codes(),), required=False)
    timezone = forms.CharField(widget=forms.Select(choices=events.timezones(), attrs=attrs_dict), max_length=200, label='Timezone (Optional)', required=False)
    telephone = forms.CharField(widget=forms.TextInput(attrs=attrs_dict), max_length=64, label='Telephone (Optional)', required=False)
    

    def clean_name(self):
        if self.cleaned_data.get('name'):
            value = self.cleaned_data['name']
            try:
                company_name = Company.objects.get(name=value)
                if company_name:
                    raise forms.ValidationError("This name has already been used, please pick a new one.")
            except Company.DoesNotExist:
                return value
