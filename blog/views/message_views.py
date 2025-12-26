"""
私人訊息相關的 Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..models import Message
from ..forms.member import MessageForm, MessageReplyForm
from ..utils.notifications import notify_message


@login_required
def inbox(request):
    """
    收件匣 - 顯示收到的訊息
    """
    # 獲取所有收到且未被收件者刪除的訊息
    received_messages = Message.objects.filter(
        recipient=request.user,
        recipient_deleted=False
    ).select_related('sender').order_by('-created_at')

    # 計算未讀數量
    unread_count = received_messages.filter(is_read=False).count()

    # 分頁處理，每頁顯示 20 則訊息
    paginator = Paginator(received_messages, 20)
    page = request.GET.get('page', 1)

    try:
        messages_list = paginator.page(page)
    except PageNotAnInteger:
        messages_list = paginator.page(1)
    except EmptyPage:
        messages_list = paginator.page(paginator.num_pages)

    context = {
        'messages_list': messages_list,
        'unread_count': unread_count,
        'total_count': paginator.count,
        'active_tab': 'inbox',
    }
    return render(request, 'blog/messages/inbox.html', context)


@login_required
def outbox(request):
    """
    寄件匣 - 顯示已發送的訊息
    """
    # 獲取所有發送且未被寄件者刪除的訊息
    sent_messages = Message.objects.filter(
        sender=request.user,
        sender_deleted=False
    ).select_related('recipient').order_by('-created_at')

    # 分頁處理，每頁顯示 20 則訊息
    paginator = Paginator(sent_messages, 20)
    page = request.GET.get('page', 1)

    try:
        messages_list = paginator.page(page)
    except PageNotAnInteger:
        messages_list = paginator.page(1)
    except EmptyPage:
        messages_list = paginator.page(paginator.num_pages)

    context = {
        'messages_list': messages_list,
        'total_count': paginator.count,
        'active_tab': 'outbox',
    }
    return render(request, 'blog/messages/outbox.html', context)


@login_required
def message_compose(request, username=None):
    """
    撰寫新訊息
    可以通過 username 參數指定收件者
    """
    recipient = None
    if username:
        recipient = get_object_or_404(User, username=username)

        # 不能發送訊息給自己
        if recipient == request.user:
            messages.error(request, '❌ 不能發送訊息給自己！')
            return redirect('inbox')

    if request.method == 'POST':
        form = MessageForm(request.POST, sender=request.user, recipient=recipient)
        if form.is_valid():
            # 獲取收件者
            recipient_username = form.cleaned_data['recipient_username']
            recipient_user = User.objects.get(username=recipient_username)

            # 建立訊息
            message = Message.objects.create(
                sender=request.user,
                recipient=recipient_user,
                subject=form.cleaned_data['subject'],
                content=form.cleaned_data['content']
            )

            # 發送通知給收件者
            notify_message(recipient_user, request.user, message)

            messages.success(request, f'✅ 訊息已發送給 {recipient_username}！')
            return redirect('outbox')
    else:
        form = MessageForm(sender=request.user, recipient=recipient)

    context = {
        'form': form,
        'recipient': recipient,
        'active_tab': 'compose',
    }
    return render(request, 'blog/messages/compose.html', context)


@login_required
def message_detail(request, message_id):
    """
    訊息詳情
    顯示訊息內容並可以回覆
    """
    # 獲取訊息
    message = get_object_or_404(Message, id=message_id)

    # 檢查權限：只有寄件者或收件者可以查看
    if message.sender != request.user and message.recipient != request.user:
        messages.error(request, '❌ 您沒有權限查看此訊息！')
        return redirect('inbox')

    # 檢查是否已被刪除
    if message.sender == request.user and message.sender_deleted:
        messages.error(request, '❌ 此訊息已被刪除！')
        return redirect('outbox')
    if message.recipient == request.user and message.recipient_deleted:
        messages.error(request, '❌ 此訊息已被刪除！')
        return redirect('inbox')

    # 如果是收件者且訊息未讀，標記為已讀
    if message.recipient == request.user and not message.is_read:
        message.mark_as_read()

    # 獲取所有回覆
    replies = Message.objects.filter(
        parent_message=message
    ).select_related('sender', 'recipient').order_by('created_at')

    # 處理回覆表單
    if request.method == 'POST':
        reply_form = MessageReplyForm(request.POST)
        if reply_form.is_valid():
            # 確定收件者（回覆給對方）
            if message.sender == request.user:
                reply_recipient = message.recipient
            else:
                reply_recipient = message.sender

            # 建立回覆訊息
            # 處理回覆標題：只在開頭沒有 "Re: " 時才添加，避免多次回覆產生多個 "Re: "
            reply_subject = message.subject
            if not reply_subject.startswith('Re: '):
                reply_subject = f'Re: {reply_subject}'

            reply = Message.objects.create(
                sender=request.user,
                recipient=reply_recipient,
                subject=reply_subject,
                content=reply_form.cleaned_data['content'],
                parent_message=message
            )

            messages.success(request, '✅ 回覆已發送！')
            return redirect('message_detail', message_id=message.id)
    else:
        reply_form = MessageReplyForm()

    context = {
        'message': message,
        'replies': replies,
        'reply_form': reply_form,
        'is_sender': message.sender == request.user,
        'is_recipient': message.recipient == request.user,
        'can_recall': message.can_recall(request.user),
    }
    return render(request, 'blog/messages/detail.html', context)


@login_required
def message_delete(request, message_id):
    """
    刪除訊息（軟刪除）
    """
    message = get_object_or_404(Message, id=message_id)

    # 檢查權限
    if message.sender != request.user and message.recipient != request.user:
        messages.error(request, '❌ 您沒有權限刪除此訊息！')
        return redirect('inbox')

    # 軟刪除：根據用戶角色設置刪除標記
    if message.sender == request.user:
        message.sender_deleted = True
        redirect_url = 'outbox'
    else:
        message.recipient_deleted = True
        redirect_url = 'inbox'

    message.save()

    # 如果雙方都刪除，則真正刪除訊息
    if message.sender_deleted and message.recipient_deleted:
        message.delete()
        messages.success(request, '✅ 訊息已永久刪除！')
    else:
        messages.success(request, '✅ 訊息已刪除！')

    return redirect(redirect_url)


@login_required
def mark_all_read(request):
    """
    標記所有訊息為已讀
    """
    Message.objects.filter(
        recipient=request.user,
        is_read=False,
        recipient_deleted=False
    ).update(is_read=True)

    messages.success(request, '✅ 所有訊息已標記為已讀！')
    return redirect('inbox')


@login_required
def message_recall(request, message_id):
    """
    收回訊息
    只有寄件者可以收回，且對方未讀的訊息才能收回
    """
    message = get_object_or_404(Message, id=message_id)

    # 檢查是否可以收回
    if not message.can_recall(request.user):
        if message.sender != request.user:
            messages.error(request, '❌ 只有寄件者可以收回訊息！')
        elif message.is_recalled:
            messages.error(request, '❌ 此訊息已經收回過了！')
        elif message.is_read:
            messages.error(request, '❌ 對方已讀的訊息無法收回！')
        else:
            messages.error(request, '❌ 無法收回此訊息！')
        return redirect('outbox')

    # 收回訊息
    message.recall()
    messages.success(request, '✅ 訊息已成功收回！')
    return redirect('outbox')


@login_required
def bulk_mark_read(request):
    """
    批次標記為已讀
    """
    if request.method == 'POST':
        message_ids = request.POST.getlist('message_ids')

        if not message_ids:
            messages.error(request, '❌ 請選擇要標記的訊息！')
            return redirect('inbox')

        # 更新訊息為已讀
        updated_count = Message.objects.filter(
            id__in=message_ids,
            recipient=request.user,
            recipient_deleted=False
        ).update(is_read=True)

        if updated_count > 0:
            messages.success(request, f'✅ 已成功標記 {updated_count} 則訊息為已讀！')
        else:
            messages.warning(request, '⚠️ 沒有訊息被更新！')

    return redirect('inbox')


@login_required
def bulk_delete(request):
    """
    批次刪除訊息（收件匣）
    """
    if request.method == 'POST':
        message_ids = request.POST.getlist('message_ids')

        if not message_ids:
            messages.error(request, '❌ 請選擇要刪除的訊息！')
            return redirect('inbox')

        # 軟刪除：標記為已刪除
        deleted_messages = Message.objects.filter(
            id__in=message_ids,
            recipient=request.user,
            recipient_deleted=False
        )

        deleted_count = 0
        for message in deleted_messages:
            message.recipient_deleted = True
            message.save()

            # 如果雙方都刪除，則真正刪除訊息
            if message.sender_deleted:
                message.delete()

            deleted_count += 1

        if deleted_count > 0:
            messages.success(request, f'✅ 已成功刪除 {deleted_count} 則訊息！')
        else:
            messages.warning(request, '⚠️ 沒有訊息被刪除！')

    return redirect('inbox')


@login_required
def outbox_bulk_delete(request):
    """
    批次刪除訊息（寄件匣）
    """
    if request.method == 'POST':
        message_ids = request.POST.getlist('message_ids')

        if not message_ids:
            messages.error(request, '❌ 請選擇要刪除的訊息！')
            return redirect('outbox')

        # 軟刪除：標記為已刪除
        deleted_messages = Message.objects.filter(
            id__in=message_ids,
            sender=request.user,
            sender_deleted=False
        )

        deleted_count = 0
        for message in deleted_messages:
            message.sender_deleted = True
            message.save()

            # 如果雙方都刪除，則真正刪除訊息
            if message.recipient_deleted:
                message.delete()

            deleted_count += 1

        if deleted_count > 0:
            messages.success(request, f'✅ 已成功刪除 {deleted_count} 則訊息！')
        else:
            messages.warning(request, '⚠️ 沒有訊息被刪除！')

    return redirect('outbox')
