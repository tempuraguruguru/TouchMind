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