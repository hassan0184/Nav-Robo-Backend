from django.contrib import admin
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter,ChoiceDropdownFilter,SimpleDropdownFilter
from rangefilter.filters import DateRangeFilter
from rider.models import Rider,TransactionHistory


@admin.register(Rider)
class RiderAdmin(admin.ModelAdmin):
    list_display = ["id", "first_name", "last_name", "current_onboard_status"]
    search_fields = ["id", "user__first_name", "user__last_name"]
    list_select_related = ['user']

@admin.register(TransactionHistory)
class TransactionHistoryAdmin(admin.ModelAdmin):
    list_display = ["status", "DateTime", "rider"]
    list_filter = (
        ('DateTime', DateRangeFilter),
        ("rider",RelatedDropdownFilter),
        ("status",ChoiceDropdownFilter),
        
    )

