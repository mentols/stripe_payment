from django.urls import path

from payment.views import CreateCheckoutSession, CancelView, SuccessView, ListProductsView, \
    BasketView, CreateCheckoutSessionOrder

urlpatterns = [
    # item's lists
    path('', ListProductsView.as_view(), name="home-page"),
    path('basket/', BasketView.as_view(), name="basket"),

    # responses after payment
    path('cancel/', CancelView.as_view()),
    path('success/', SuccessView.as_view()),

    # checkouts for payment
    path('buy/<int:pk>/', CreateCheckoutSession.as_view(), name="create-checkout-session"),
    path('buy_order/<int:pk>/', CreateCheckoutSessionOrder.as_view(), name="create-checkout-session-order"),
]
