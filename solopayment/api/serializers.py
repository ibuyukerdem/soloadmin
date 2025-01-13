# -----------------------------------------------------------------------------
# solopayment/api/serializers.py
# -----------------------------------------------------------------------------
"""
Bu dosya, e-tahsilat sistemindeki modellerin (PaymentProvider, PaymentMethod, 
PaymentFee, PaymentTransaction) için DRF serializer tanımlarını içerir.

Model alanlarının ne şekilde API'ye yansıyacağını kontrol etmek amacıyla 
BaseDateTimeSerializer veya BaseOnlyDateSerializer soyutlamaları kullanılabilir.
"""

from rest_framework import serializers
from common.base_serializer import BaseDateTimeSerializer
# Yukarıdaki import, BaseDateTimeSerializer veya BaseOnlyDateSerializer olabilir.

from solopayment.models import (
    PaymentProvider,
    PaymentMethod,
    PaymentFee,
    PaymentTransaction
)


class PaymentProviderSerializer(BaseDateTimeSerializer):
    """
    PaymentProvider, AbstractBaseModel'den miras almayan bir modeldir.
    Bu nedenle site, createdAt, updatedAt gibi alanlar yoktur (ama createDate, updateDate vardır).
    """
    class Meta:
        model = PaymentProvider
        fields = [
            'id', 'providerName', 'providerCode',
            'description', 'isActive',
            'createDate', 'updateDate'
        ]


class PaymentMethodSerializer(BaseDateTimeSerializer):
    """
    PaymentMethod, AbstractBaseModel'den miras aldığı için site, createdAt, updatedAt alanlarını da içerir.
    """
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'site',
            'merchantUser', 'paymentProvider',
            'defaultForSingleShot', 'commissionPayer', 'isActive',
            'credentials',
            'createdAt', 'updatedAt'
        ]


class PaymentFeeSerializer(BaseDateTimeSerializer):
    """
    PaymentFee, AbstractBaseModel.
    """
    class Meta:
        model = PaymentFee
        fields = [
            'id', 'site',
            'paymentMethod', 'installmentCount',
            'fixedFee', 'percentageFee', 'isActive',
            'createdAt', 'updatedAt'
        ]


class PaymentTransactionSerializer(BaseDateTimeSerializer):
    """
    PaymentTransaction, AbstractBaseModel.
    """
    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'site',
            'merchantUser', 'payingUser',
            'payerName', 'payerNote',
            'paymentMethod', 'amount', 'installmentCount', 'totalPaidAmount',
            'status', 'referenceCode',
            'calculatedFixedFee', 'calculatedPercentageFee',
            'createdAt', 'updatedAt'
        ]