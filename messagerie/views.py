from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import Message
from .forms import MessageForm, CommentForm

@login_required
def message_list(request):
    qs = Message.objects.select_related('author').prefetch_related('mentions')
    return render(request, 'messagerie/message_list.html', {'messages': qs})

@login_required
def message_detail(request, pk):
    msg = get_object_or_404(Message, pk=pk)

    # Marquer comme lu
    msg.read_by.add(request.user)

    # commentaire
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.author = request.user
            c.message = msg
            c.save()
            return redirect('messagerie:message_detail', pk=pk)
    else:
        form = CommentForm()
    return render(request, 'messagerie/message_detail.html', {
        'message': msg,
        'form': form,
    })

@login_required
def message_create(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            m = form.save(commit=False)
            m.author = request.user
            m.save()
            form.save_m2m()  # pour mentions
            return redirect('messagerie:message_list')
    else:
        form = MessageForm()
    return render(request, 'messagerie/message_form.html', {'form': form})

@login_required
def message_edit(request, pk):
    msg = get_object_or_404(Message, pk=pk)
    if msg.author != request.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = MessageForm(request.POST, instance=msg)
        if form.is_valid():
            form.save()
            return redirect('messagerie:message_detail', pk=pk)
    else:
        form = MessageForm(instance=msg)
    return render(request, 'messagerie/message_form.html', {
        'form': form,
        'edit': True,          # permet d'ajuster le titre du formulaire
        'message_obj': msg,
    })

@login_required
def message_delete(request, pk):
    msg = get_object_or_404(Message, pk=pk)
    if msg.author != request.user:
        return HttpResponseForbidden()
    # Suppression immédiate et redirection vers la liste
    msg.delete()
    return redirect('messagerie:message_list')