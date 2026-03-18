from django import forms
from seller.models import Attribute, AttributeOption, ProductVariant, VariantAttributeBridge
from core.models import Category, SubCategory, Banner


class AttributeForm(forms.ModelForm):
    """Form for creating and editing Product Attributes"""
    
    subcategory = forms.ModelChoiceField(
        queryset=SubCategory.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2.5 border border-muted/50 rounded-xl text-sm focus:outline-none focus:border-dark bg-white'
        }),
        required=False,
        label="Subcategory (Optional)"
    )
    
    class Meta:
        model = Attribute
        fields = ['name', 'subcategory']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-muted/50 rounded-xl text-sm focus:outline-none focus:border-dark',
                'placeholder': 'e.g., Color, Size, Material',
                'required': True
            }),
        }
        labels = {
            'name': 'Attribute Name',
        }


class AttributeOptionForm(forms.ModelForm):
    """Form for creating and editing Attribute Options"""
    
    attribute = forms.ModelChoiceField(
        queryset=Attribute.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2.5 border border-muted/50 rounded-xl text-sm focus:outline-none focus:border-dark bg-white'
        }),
        label="Select Attribute"
    )
    
    class Meta:
        model = AttributeOption
        fields = ['attribute', 'value']
        widgets = {
            'value': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-muted/50 rounded-xl text-sm focus:outline-none focus:border-dark',
                'placeholder': 'e.g., Red, XL, Cotton',
                'required': True
            }),
        }
        labels = {
            'value': 'Option Value',
        }


class CategoryForm(forms.ModelForm):
    """Form for creating and editing Categories"""

    class Meta:
        model = Category
        fields = ['name', 'image_url', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-muted/50 rounded-xl text-sm focus:outline-none focus:border-dark',
                'placeholder': 'e.g., Electronics',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 border border-muted/50 rounded-xl text-sm focus:outline-none focus:border-dark',
                'rows': 3,
                'placeholder': 'Short category description (optional)'
            }),
        }
        labels = {
            'name': 'Category Name',
            'image_url': 'Category Image',
            'description': 'Description',
            'is_active': 'Active',
        }


class SubCategoryForm(forms.ModelForm):
    """Form for creating and editing SubCategories"""

    category = forms.ModelChoiceField(
        queryset=SubCategory._meta.get_field('category').related_model.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2.5 border border-muted/50 rounded-xl text-sm focus:outline-none focus:border-dark bg-white'
        }),
        label='Select Category',
        required=True,
    )

    class Meta:
        model = SubCategory
        fields = ['category', 'name', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-muted/50 rounded-xl text-sm focus:outline-none focus:border-dark',
                'placeholder': 'e.g., Mobile Phones',
                'required': True
            }),
        }
        labels = {
            'name': 'SubCategory Name',
            'is_active': 'Active',
        }




class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['title', 'image_url', 'redirect_url', 'start_date', 'end_date', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-muted/50 rounded-xl text-sm', 'placeholder': 'Banner Title'}),
            'redirect_url': forms.URLInput(attrs={'class': 'w-full px-4 py-2.5 border border-muted/50 rounded-xl text-sm', 'placeholder': 'Redirect URL'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2.5 border border-muted/50 rounded-xl text-sm'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2.5 border border-muted/50 rounded-xl text-sm'}),
        }


class VariantAttributeBridgeForm(forms.ModelForm):
    variant = forms.ModelChoiceField(
        queryset=ProductVariant.objects.all(),
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2.5 border border-muted/50 rounded-xl text-sm bg-white'}),
        label='Product Variant'
    )
    option = forms.ModelChoiceField(
        queryset=AttributeOption.objects.all(),
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2.5 border border-muted/50 rounded-xl text-sm bg-white'}),
        label='Attribute Option'
    )

    class Meta:
        model = VariantAttributeBridge
        fields = ['variant', 'option']



