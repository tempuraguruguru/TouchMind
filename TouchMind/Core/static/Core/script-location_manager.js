// CSRFトークン取得関数
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

// グローバル変数：読み込んだ場所データを保持しておく
let locationsData = [];

document.addEventListener("DOMContentLoaded", loadExistingLocations);

// 一覧データの読み込みと描画
function loadExistingLocations() {
    fetch('/api/get-locations/')
        .then(res => res.json())
        .then(data => {
            locationsData = data.locations; // データを保存
            const tbody = document.getElementById('existing-tbody');
            tbody.innerHTML = '';

            data.locations.forEach(loc => {
                // カテゴリの表示変換
                let catText = loc.category === 'work' ? '💻 ワーク' :
                              loc.category === 'relax' ? '☕ リラックス' :
                              loc.category === 'pokemon' ? '🎮 ポケモン' : '🚃 移動';

                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${loc.tag_id}</strong></td>
                    <td>${loc.name}</td>
                    <td>${catText}</td>
                    <td><div class="desc-preview">${loc.description}</div></td>
                    <td>
                        <button class="btn btn-primary" style="padding: 4px 8px; font-size: 12px;"
                                onclick="openSidebar('edit', '${loc.tag_id}')">✏️ 修正</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        });
}

// --------------------------------------------------------
// サイドバーの制御
// --------------------------------------------------------
function openSidebar(mode, tagId = '') {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const title = document.getElementById('sidebar-title');
    const formMode = document.getElementById('form-mode');

    // フォームのリセット
    document.getElementById('sb-tag-id').value = '';
    document.getElementById('sb-name').value = '';
    document.getElementById('sb-category').value = 'work';
    document.getElementById('sb-desc').value = '';

    formMode.value = mode;

    if (mode === 'create') {
        title.innerText = '➕ 新規場所の登録';
        document.getElementById('sb-tag-id').readOnly = false;
        document.getElementById('keep-open-wrapper').style.display = 'block'; // 連続追加を表示
    } else if (mode === 'edit') {
        title.innerText = '✏️ 場所の編集';
        document.getElementById('sb-tag-id').readOnly = true; // 編集時はTag IDをロック
        document.getElementById('keep-open-wrapper').style.display = 'none'; // 連続追加を隠す

        // 既存のデータをフォームに流し込む
        const loc = locationsData.find(l => l.tag_id === tagId);
        if (loc) {
            document.getElementById('sb-tag-id').value = loc.tag_id;
            document.getElementById('sb-name').value = loc.name;
            document.getElementById('sb-category').value = loc.category;
            document.getElementById('sb-desc').value = loc.description;
        }
    }

    sidebar.classList.add('open');
    overlay.classList.add('open');
}

function closeSidebar() {
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('sidebar-overlay').classList.remove('open');
}

// 保存ボタンを押したときの処理
function saveLocation() {
    const mode = document.getElementById('form-mode').value;
    const tagId = document.getElementById('sb-tag-id').value.trim();
    const name = document.getElementById('sb-name').value.trim();
    const category = document.getElementById('sb-category').value;
    const description = document.getElementById('sb-desc').value.trim();

    if (!tagId) {
        alert("Tag IDは必須です。");
        return;
    }

    const payload = {
        tag_id: tagId,
        name: name,
        category: category,
        description: description
    };

    let url = '';
    let bodyData = {};

    if (mode === 'create') {
        url = '/api/bulk-add-locations/';
        bodyData = { locations: [payload] }; // 新規作成APIは配列を期待しているため包む
    } else {
        url = '/api/update-location/';
        bodyData = payload; // 更新APIは単体オブジェクトを期待している
    }

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(bodyData)
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            loadExistingLocations(); // 一覧を更新

            // 「続けて登録する」にチェックが入っていればフォームを空にして待機
            const keepOpen = document.getElementById('sb-keep-open').checked;
            if (mode === 'create' && keepOpen) {
                document.getElementById('sb-tag-id').value = '';
                document.getElementById('sb-name').value = '';
                document.getElementById('sb-desc').value = '';
                document.getElementById('sb-tag-id').focus();
            } else {
                closeSidebar();
            }
        } else {
            alert(data.message);
        }
    })
    .catch(err => console.error(err));
}