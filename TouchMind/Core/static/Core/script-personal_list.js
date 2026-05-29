// CSRFトークンを取得する関数（場所管理画面と同じ仕組み）
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

// 思考ログを削除する関数
function deleteEvent(eventId) {
    if (!confirm('この思考ログを削除しますか？\n（ネットワーク図からも消えます）')) {
        return;
    }

    fetch('/api/delete-event/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ event_id: eventId })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            // カードではなく「テーブルの行」を取得してフワッと消す
            const row = document.getElementById(`event-row-${eventId}`);
            if (row) {
                row.style.opacity = '0';
                setTimeout(() => {
                    row.remove();
                }, 300);
            }
        } else {
            alert(data.message);
        }
    })
    .catch(err => console.error('削除エラー:', err));
}