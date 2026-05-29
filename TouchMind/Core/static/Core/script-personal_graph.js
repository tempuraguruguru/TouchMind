let nodes = [];
let links = [];
let nodeMap = {};
let energy = 1.0;

let draggedNode = null;
let offsetX = 0;
let offsetY = 0;
let isDraggingNetwork = false;
let dragStartX, dragStartY;

function preload() {
    // APIの向き先をパーソナル用に変更
    fetch('/api/personal-graph-data/')
        .then(response => response.json())
        .then(data => {
            initGraph(data.nodes, data.links);
        });
}


function setup() {
    // 1. キャンバスを変数に格納する
    let canvas = createCanvas(windowWidth, windowHeight - 50);

    // 2. キャンバスを id="content-area" のDIVの中に配置する
    canvas.parent('content-area');

    textAlign(CENTER, CENTER);
    textSize(12);
}


function initGraph(rawNodes, rawLinks) {
    // ノードの数に合わせて角度を計算し、円状に並べる
    let angleStep = TWO_PI / rawNodes.length;
    let radius = Math.min(width, height) * 0.3; // 広がる前の初期範囲

    rawNodes.forEach((n, index) => {
        let angle = random(TWO_PI);
        let r = random(radius); // 0〜radiusのランダムな距離

        let isLocation = (n.group && n.group.includes('location'));
        let nodeSize = n.group.includes('location') ? 50 : 30;

        let node = {
            id: n.id, label: n.label, group: n.group,
            detail: n.detail,
            category: n.category,
            x: width / 2 + Math.cos(angle) * r,
            y: height / 2 + Math.sin(angle) * r,
            vx: 0, vy: 0,
            size: nodeSize
        };
        nodes.push(node);
        nodeMap[n.id] = node;
    });

    rawLinks.forEach(l => {
        links.push({
            source: nodeMap[l.source],
            target: nodeMap[l.target]
        });
    });
}


function draw() {
    background('#f0f4f8');

    if (nodes.length === 0) return;

    energy *= 0.99;
    if (energy < 0.01) energy = 0;

    let k = 0.05 * energy;
    let repulsion = 1000 * energy;
    let damping = 0.5;

    for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
            let dx = nodes[i].x - nodes[j].x;
            let dy = nodes[i].y - nodes[j].y;
            let distSq = dx * dx + dy * dy;

            if (distSq < 2500) distSq = 2500;

            if (distSq > 0 && distSq < 90000) {
                let force = repulsion / distSq;
                let fx = force * dx;
                let fy = force * dy;
                nodes[i].vx += fx; nodes[i].vy += fy;
                nodes[j].vx -= fx; nodes[j].vy -= fy;
            }
        }
    }

    let restLength = 100;
    for (let l of links) {
        let dx = l.target.x - l.source.x;
        let dy = l.target.y - l.source.y;
        let dist = Math.sqrt(dx * dx + dy * dy) + 0.1;

        let force = (dist - restLength) * k;
        let fx = (dx / dist) * force;
        let fy = (dy / dist) * force;

        l.source.vx += fx; l.source.vy += fy;
        l.target.vx -= fx; l.target.vy -= fy;
    }

    for (let n of nodes) {
        n.vx += (width / 2 - n.x) * 0.001 * energy;
        n.vy += (height / 2 - n.y) * 0.001 * energy;
    }

    push();
    translate(offsetX, offsetY);

    stroke(180);
    strokeWeight(1);
    for (let l of links) {
        line(l.source.x, l.source.y, l.target.x, l.target.y);
    }

    noStroke();
    for (let n of nodes) {
        if (n !== draggedNode) {
            let maxV = 8;
            n.vx = constrain(n.vx, -maxV, maxV);
            n.vy = constrain(n.vy, -maxV, maxV);

            n.x += n.vx; n.y += n.vy;
            n.vx *= damping; n.vy *= damping;

            if (Math.abs(n.vx) < 0.05) n.vx = 0;
            if (Math.abs(n.vy) < 0.05) n.vy = 0;
        }

        // 色分け処理
        if (n.group === 'user') fill(255, 100, 100);
        else if (n.group === 'location' || n.group === 'visited_location') fill(100, 150, 255);
        else if (n.group === 'unvisited_location') fill(200, 200, 200);
        else fill(100, 200, 100);

        // もし size が undefined なら強制的に 30 にする（画面から消えるのを防ぐ）
        let s = n.size || 30;

        // 固定の30ではなく、n.size を使う
        ellipse(n.x, n.y, n.size, n.size);

        // 文字が円に被らないように、サイズに合わせて少し下にズラす
        fill(50);
        text(n.label, n.x, n.y + (n.size / 2) + 12);
    }
    pop();
}


// --- マウスイベント処理 ---
function mousePressed() {
    let mx = mouseX - offsetX;
    let my = mouseY - offsetY;
    let nodeClicked = false;
    let detailPanel = document.getElementById('detail-panel');

    for (let n of nodes) {
        // if (!showUserNodes && n.group === 'user') continue;

        // 固定の15ではなく、そのノードの半径(n.size / 2)で当たり判定をする
        if (dist(mx, my, n.x, n.y) < n.size / 2) {
            draggedNode = n;
            energy = 1.0;
            nodeClicked = true;

            // クリックしたのが場所ノードなら詳細パネルを表示
            if (n.group.includes('location')) {
                document.getElementById('detail-title').innerText = n.label;

                // カテゴリの日本語表記変換（簡易版）
                let catText = n.category === 'work' ? '💻 ワーク' :
                              n.category === 'relax' ? '☕ リラックス' :
                              n.category === 'transit' ? '🚃 移動' : '📍 未分類';

                document.getElementById('detail-category').innerText = catText;
                document.getElementById('detail-desc').innerText = n.detail || "詳細情報がありません。";

                // ノードのIDは "tag_desk_01" のようになっているため、先頭の "tag_" を取り除いて純粋なIDにします
                let actualTagId = n.id.replace('tag_', '');

                // href属性ではなく、クリックイベントで強制的に遷移させる
                let recordBtn = document.getElementById('detail-record-btn');
                recordBtn.onclick = function(e) {
                    e.stopPropagation(); // 念のためここでもイベント伝播をストップ
                    window.location.href = `/?tag_id=${actualTagId}`;
                };

                detailPanel.style.display = 'block'; // パネルを表示
            } else {
                detailPanel.style.display = 'none'; // 思考ノードなどをクリックしたら隠す
            }

            break;
        }
    }

    if (!nodeClicked) {
        isDraggingNetwork = true;
        dragStartX = mouseX - offsetX;
        dragStartY = mouseY - offsetY;
        detailPanel.style.display = 'none'; // 何もない背景をクリックしても隠す
    }
}


function mouseDragged() {
    if (draggedNode) {
        draggedNode.x = mouseX - offsetX;
        draggedNode.y = mouseY - offsetY;
        draggedNode.vx = 0;
        draggedNode.vy = 0;
        if (energy < 0.2) energy = 0.2;
    }
    else if (isDraggingNetwork) {
        offsetX = mouseX - dragStartX;
        offsetY = mouseY - dragStartY;
    }
}


function mouseReleased() {
    draggedNode = null;
    isDraggingNetwork = false;
}


function windowResized() {
    // リサイズ時もヘッダーの分(50px)を引く
    resizeCanvas(windowWidth, windowHeight - 50);
}


function keyPressed() {
    // スペースキーが押されたら、ネットワークを揺らす（シェイク）
    if (key === ' ') {
        energy = 1.0; // 熱量をMAXに戻す
        for (let n of nodes) {
            // 各ノードにランダムな強い衝撃を与えて、局所的な絡まりを吹き飛ばす
            n.vx += random(-100, 100);
            n.vy += random(-100, 100);
        }
    }
}