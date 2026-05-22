document.getElementById('sendButton').addEventListener('click', async ()=> {
    const text = document.getElementById('thoughtInput').value; // ユーザーが考えたこと
    const status = document.getElementById('status'); // システムの状態

    // tag_idをJavaScriptの変数に格納
    const currentTagId = window.CURRENT_TAG_ID;

    if(!text){
        status.innerText = "テキストを入力してください";
        return;
    }

    status.innerText = "送信中...";

    try{
        // Django APIへ送信(views.record_event)
        const responce = await fetch('/api/record/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ tag_id: currentTagId, text: text })
        });

        if(responce.ok){
            status.innerText = "記録完了！画面を閉じてOKです";
            document.getElementById('thoughtInput').value = ""; // 記録完了したのでボタンを空にする
        }else{
            status.innerText = "エラーが発生しました";
        }
    }catch(error){
        status.innerText = "エラー: " + error;
    }
});


document.addEventListener("DOMContentLoaded", function() {
    const urlParams = new URLSearchParams(window.location.search);
    const tagId = urlParams.get('tag_id');

    // ★テスト用に、tagIdがなくても強制的にカードを表示させる場合は下のコメントアウトを外します
    // document.getElementById('personalized-card').style.display = 'block';

    if (tagId) {
        console.log(`📡 APIへ通信開始: /api/personalized-suggestion/?tag_id=${tagId}`);

        // ローディングを見せるためにカードを表示
        const card = document.getElementById('personalized-card');
        card.style.display = 'block';

        fetch(`/api/personalized-suggestion/?tag_id=${tagId}`)
            .then(response => {
                console.log("📥 サーバーからのステータス:", response.status);
                if (!response.ok) {
                    throw new Error(`サーバーエラー: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("📦 サーバーからのデータ:", data);
                if (data.message) {
                    document.getElementById('suggestion-title').innerText = data.title;
                    document.getElementById('suggestion-message').innerText = data.message;
                } else {
                    document.getElementById('suggestion-message').innerText = "提案データが見つかりませんでした。";
                }
            })
            .catch(err => {
                console.error("❌ 通信エラー詳細:", err);
                document.getElementById('suggestion-title').innerText = "⚠️ エラー発生";
                document.getElementById('suggestion-message').innerText = "通信に失敗しました。F12キーを押してコンソール(Console)を確認してください。";
            });
    }
});