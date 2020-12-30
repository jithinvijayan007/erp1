from rest_framework import serializers
from pricelist.models import PriceList

class PriceListSerializer(serializers.ModelSerializer):

    fk_item__vchr_item_code = serializers.CharField(read_only=True)
    fk_item__vchr_name = serializers.CharField(read_only=True)
    vchr_item_name = serializers.CharField(read_only=True)
    fk_item__fk_brand_id = serializers.IntegerField(read_only=True)
    fk_item__fk_brand__vchr_name  = serializers.CharField(read_only=True)
    fk_item__fk_product_id  = serializers.IntegerField(read_only=True)
    fk_item__fk_product__vchr_name = serializers.CharField(read_only=True)
    str_formatted_date = serializers.CharField(read_only=True)

    class Meta:
        model = PriceList
        fields =[
            'dat_efct_from',
            'dbl_supp_amnt',
            'dbl_cost_amnt',
            'dbl_mop',
            'dbl_mrp',
            'dbl_my_amt',
            'dbl_dealer_amt',
            'vchr_item_name',
            'fk_item__vchr_item_code',
            'fk_item__vchr_name',
            'fk_item__fk_brand_id',
            'fk_item__fk_brand__vchr_name',
            'fk_item__fk_product_id',
            'fk_item__fk_product__vchr_name',
            'str_formatted_date'



                ]
