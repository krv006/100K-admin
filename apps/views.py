import re

from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Max, F
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, FormView, UpdateView
from django.views.generic import TemplateView

from apps.form import OrderForm, StreamForm
from apps.models import Category, Product, Stream, SiteSettings, Order, Region
from apps.models import User

from django.urls import reverse_lazy


# Create your views here.

def search_products(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.all()
    return render(request, 'apps/profile/sections/search.html', {'products': products, 'query': query})


class HomeListView(ListView):
    queryset = Product.objects.order_by('-created_at')
    template_name = 'apps/product/home.html'
    context_object_name = 'products'
    paginate_by = 8

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        category_id = self.request.GET.get('category')
        if category_id:
            context['categories'] = Category.objects.filter(parent_id=category_id)
        else:
            context['categories'] = Category.objects.all()
        return context


class ProductListView(ListView):
    queryset = Product.objects.prefetch_related('images').all()
    template_name = 'apps/product/product-list.html'
    context_object_name = 'products'

    def get_image(self, product):
        image = product.images.first()
        print(image)
        if image:
            return image.image.url
        print(image)
        return '/path/to/default/image.jpg'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.GET.get('category'):
            queryset = queryset.filter(category_id=self.request.GET.get('category'))
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'apps/product/product-detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        qs = super().get_context_data(**kwargs)
        qs["regions"] = Region.objects.all()
        return qs


class ContactView(LoginRequiredMixin, TemplateView):
    template_name = 'apps/profile/contacts.html'


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'apps/profile/profile.html'


class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'apps/profile/sections/dashboard.html'


class AdminStreamView(LoginRequiredMixin, TemplateView):
    template_name = 'apps/profile/sections/stream.html'


class AdminStatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'apps/profile/sections/statistics.html'


class AdminPaymentView(LoginRequiredMixin, TemplateView):
    template_name = 'apps/profile/sections/payment.html'


class CustomLoginView(TemplateView):
    template_name = 'apps/auth/login.html'

    def post(self, request, *args, **kwargs):
        phone_number = re.sub(r'\D', '', request.POST.get('phone_number', ''))
        user = User.objects.filter(phone_number=phone_number).first()

        if len(phone_number) < 10:
            context = {
                "messages_error": ["Invalid phone number"]
            }
            return render(request, self.template_name, context)
            # send_email

        if not user:
            user = User.objects.create_user(phone_number=phone_number, password=request.POST.get('password'))
            login(request, user)
            return redirect('home')

        user = authenticate(request, username=user.phone_number, password=request.POST.get('password'))
        if user:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            context = {
                "messages_error": ["Invalid password"]
            }
            return render(request, self.template_name, context)


# TODO celery bn qivoramiz


class ProductDetailDetailView(DetailView):
    model = Product
    template_name = 'apps/product/product-detail.html'
    context_object_name = 'product'


class StreamListView(LoginRequiredMixin, ListView):
    template_name = 'apps/profile/sections/stream.html'
    queryset = Stream.objects.all()
    context_object_name = 'streams'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class StreamFormView(FormView):
    form_class = StreamForm
    template_name = 'apps/profile/sections/market.html'

    def form_valid(self, form):
        form.save()
        return redirect('stream')

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class StreamDetailView(DetailView):
    queryset = Product.objects.all()
    template_name = 'apps/profile/sections/stream.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['self_stream'] = Stream.objects.filter(product=self.object, owner=self.request.user)
        return context


class StreamOrderView(DetailView, FormView):
    form_class = OrderForm
    queryset = Stream.objects.all()
    template_name = 'apps/product/product-detail.html'
    context_object_name = 'stream'

    def form_valid(self, form):
        if form.is_valid():
            form = form.save(commit=False)
            form.stream = self.get_object()
            form.user = self.request.user
            form.save()
            form.product.price -= self.get_object().discount
            form.deliver_price = SiteSettings.objects.first().deliver_price
        return render(self.request, 'apps/product/product-order.html', {'form': form})

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object.product
        product.price -= self.object.discount
        context['product'] = product
        context["regions"] = Region.objects.all()
        stream_id = self.kwargs.get('pk')
        Stream.objects.filter(pk=stream_id).update(count=F('count') + 1)
        return context


class AdminMarketView(LoginRequiredMixin, ListView):
    template_name = 'apps/profile/sections/market.html'
    queryset = Category.objects.all()
    context_object_name = 'categories'

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        products = Product.objects.all()
        if slug := self.request.GET.get("category"):
            products = products.filter(category__slug=slug)
        data['products'] = products
        return data


class OrderCreateView(LoginRequiredMixin, CreateView):
    template_name = 'apps/product/product-detail.html'

    def get(self, request, product_id, **kwargs):
        product = get_object_or_404(Product, id=product_id)
        regions = Region.objects.all()  # Region obyektlarini olish
        return render(request, self.template_name, {'product': product, 'regions': regions})

    def post(self, request, product_id, **kwargs):
        product = get_object_or_404(Product, id=product_id)
        region_id = request.POST.get('region')

        if not region_id:
            context = {
                "messages_error": ["Hudud tanlanmagan. Iltimos, hududni tanlang."],
                "product": product
            }
            return render(request, self.template_name, context=context)

        region = get_object_or_404(Region, id=region_id)  # Region obyektini olish
        order = Order(
            name=request.POST.get('name'),
            phone_number=re.sub(r'\D', '', request.POST.get('phone_number')),
            region=region,
            product=product
        )
        try:
            order.clean()
        except ValidationError as e:
            context = {
                "messages_error": [e.message],
                "product": product
            }
            return render(request, self.template_name, context=context)

        order.save()
        return redirect('order_success', order_id=order.id)


class OrderListView(LoginRequiredMixin, ListView):
    template_name = 'apps/product/product-order.html'  # Sizning shablon nomi
    context_object_name = 'orders'

    def get(self, request, order_id, **kwargs):
        order = get_object_or_404(Order, id=order_id)
        products = Product.objects.all()
        return render(request, self.template_name, context={'order': order, 'products': products})

    def get_queryset(self):
        # Agar siz faqat hozirgi foydalanuvchi buyurtmalarini ko'rsatmoqchi bo'lsangiz
        return Order.objects.filter(user=self.request.user)


class OrderedListView(ListView):
    model = Order
    template_name = 'apps/product/product-archived.html'
    context_object_name = 'orders'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = self.get_queryset()  # or self.queryset
        return context


class SettingsUpdateView(LoginRequiredMixin, UpdateView):
    queryset = User.objects.all()
    fields = 'first_name', 'last_name'
    template_name = 'apps/profile/profile.html'
    success_url = reverse_lazy('settings_page')

    def get_object(self, queryset=None):
        return self.request.user

