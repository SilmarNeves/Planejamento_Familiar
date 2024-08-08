from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Transacao, Categoria, SaldosFaturas
from .forms import TransacaoForm, CategoriaForm
from django.db.models import Sum, Q
from django.utils import timezone
import calendar
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from decimal import Decimal

class TransacaoListView(ListView):
    model = Transacao
    template_name = 'app_financas/transacao_list.html'
    context_object_name = 'transacoes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = timezone.now()
        context['ano'] = hoje.year
        context['mes'] = hoje.strftime('%B')
        context['entradas'] = Transacao.objects.filter(tipo='entrada').aggregate(Sum('valor'))['valor__sum'] or 0
        context['saidas'] = Transacao.objects.filter(tipo='saida').aggregate(Sum('valor'))['valor__sum'] or 0
        context['saldo'] = context['entradas'] - context['saidas']
        return context

class TransacaoCreateView(CreateView):
    model = Transacao
    form_class = TransacaoForm
    template_name = 'app_financas/transacao_form.html'
    success_url = reverse_lazy('transacao_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.order_fields(['data', 'tipo', 'descricao', 'categoria', 'valor'])
        return form

class TransacaoUpdateView(UpdateView):
    model = Transacao
    form_class = TransacaoForm
    template_name = 'app_financas/transacao_form.html'
    success_url = reverse_lazy('transacao_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.order_fields(['data', 'tipo', 'descricao', 'categoria', 'valor'])
        return form

class CategoriaListView(ListView):
    model = Categoria
    template_name = 'app_financas/categoria_list.html'
    context_object_name = 'categorias'
    ordering = ['nome']

class CategoriaCreateView(CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'app_financas/categoria_form.html'
    success_url = reverse_lazy('categoria_list')

class CategoriaUpdateView(UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'app_financas/categoria_form.html'
    success_url = reverse_lazy('categoria_list')

class CategoriaDeleteView(DeleteView):
    model = Categoria
    template_name = 'app_financas/categoria_confirm_delete.html'
    success_url = reverse_lazy('categoria_list')

@require_POST
@login_required
def salvar_saldos_faturas(request):
    SaldosFaturas.objects.create(
        saldo_bradesco=request.POST.get('saldo_bradesco'),
        saldo_itau=request.POST.get('saldo_itau'),
        saldo_inter=request.POST.get('saldo_inter'),
        fatura_bradesco=request.POST.get('fatura_bradesco'),
        fatura_itau=request.POST.get('fatura_itau'),
        fatura_inter=request.POST.get('fatura_inter'),
    )
    return JsonResponse({'status': 'success'})

def resumo(request):
    ano = request.GET.get('ano', timezone.now().year)
    mes = request.GET.get('mes', timezone.now().month)

    primeiro_dia = timezone.datetime(int(ano), int(mes), 1)
    ultimo_dia = timezone.datetime(int(ano), int(mes), calendar.monthrange(int(ano), int(mes))[1])
    
    entradas = Transacao.objects.filter(data__range=[primeiro_dia, ultimo_dia], tipo='entrada').aggregate(Sum('valor'))['valor__sum'] or 0
    saidas = Transacao.objects.filter(data__range=[primeiro_dia, ultimo_dia], tipo='saida').aggregate(Sum('valor'))['valor__sum'] or 0
    
    latest_saldos_faturas = SaldosFaturas.objects.order_by('-data_atualizacao').first()
    total_faturas = latest_saldos_faturas.fatura_bradesco + latest_saldos_faturas.fatura_itau + latest_saldos_faturas.fatura_inter if latest_saldos_faturas else 0
    
    saidas_total = saidas + total_faturas

    saldo = entradas - saidas
    
    acumulado = Transacao.objects.filter(data__lte=ultimo_dia).aggregate(
        acumulado=Sum('valor', filter=Q(tipo='entrada')) - Sum('valor', filter=Q(tipo='saida'))
    )['acumulado'] or 0

    meses = list(range(1, 13))
    anos = list(range(2023, 2027))

    context = {
        'ano': ano,
        'mes': mes,
        'entradas': float(entradas),
        'saidas': float(saidas),
        'saldo': float(saldo),
        'acumulado': float(acumulado),
        'meses': meses,
        'anos': anos,
        'mes_selecionado': int(mes),
        'ano_selecionado': int(ano),
        'saidas_total': float(saidas_total),
        'latest_saldos_faturas': latest_saldos_faturas,
    }
    
    return render(request, 'app_financas/resumo.html', context)
