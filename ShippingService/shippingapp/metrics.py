from prometheus_client import CollectorRegistry, Gauge, generate_latest, CONTENT_TYPE_LATEST
from django.http import HttpResponse

registry = CollectorRegistry()
health_gauge = Gauge('shipping_service_health', 'Health status of the shipping service', registry=registry)

def metrics(request):
    # Simple example — 1 means healthy
    health_gauge.set(1)
    return HttpResponse(generate_latest(registry), content_type=CONTENT_TYPE_LATEST)

