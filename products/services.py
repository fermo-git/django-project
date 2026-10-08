from decimal import Decimal, ROUND_HALF_UP

from .models import Product


class EstrategiaDescuento:
    porcentaje = Decimal('0')

    def calcular_precio_final(self, precio):
        descuento = precio * self.porcentaje / Decimal('100')
        return (precio - descuento).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP,
        )


class DescuentoElectronica(EstrategiaDescuento):
    porcentaje = Decimal('10')


class DescuentoRopa(EstrategiaDescuento):
    porcentaje = Decimal('15')


class SinDescuento(EstrategiaDescuento):
    porcentaje = Decimal('0')


def obtener_estrategia_descuento(category_name):
    normalized_name = category_name.strip().casefold()
    if normalized_name in {'electronica', 'electrónica'}:
        return DescuentoElectronica()
    if normalized_name == 'ropa':
        return DescuentoRopa()
    return SinDescuento()


class ProductosFacade:
    def obtener_precios_finales(self):
        products = Product.objects.select_related('category').order_by('id')
        results = []

        for product in products:
            strategy = obtener_estrategia_descuento(product.category.name)
            results.append({
                'id': product.id,
                'name': product.name,
                'category': product.category.name,
                'original_price': product.price,
                'discount_percentage': int(strategy.porcentaje),
                'final_price': strategy.calcular_precio_final(product.price),
            })

        return results
