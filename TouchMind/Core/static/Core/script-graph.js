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
    fetch('/api/graph-data/')
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
        // ★変更：規則的な角度計算をやめ、中心付近のランダムな位置に配置する
        let angle = random(TWO_PI);
        let r = random(radius); // 0〜radiusのランダムな距離

        // グループ名に 'location' が含まれていればサイズ50、それ以外は30
        // n.groupが空っぽ（undefined）でもエラーにならないように安全策を追加
        let isLocation = (n.group && n.group.includes('location'));
        let nodeSize = n.group.includes('location') ? 50 : 30;

        let node = {
            id: n.id, label: n.label, group: n.group,
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

    // 1. 斥力
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

    // 2. 引力
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

    // 3. 中心への引力
    for (let n of nodes) {
        n.vx += (width / 2 - n.x) * 0.0005 * energy;
        n.vy += (height / 2 - n.y) * 0.0005 * energy;
    }

    // --- 画面の描画だけをズラす（カメラの移動） ---
    push(); // 現在の描画状態を保存
    translate(offsetX, offsetY); // 画面全体をマウスのドラッグ量に合わせて移動

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
    pop(); // 描画状態を元に戻す（これがないとUIまでズレてしまう）
}


// --- マウスイベント処理 ---
function mousePressed() {
    // マウスの座標からカメラのズレ（オフセット）を引いて、真の座標を計算
    let mx = mouseX - offsetX;
    let my = mouseY - offsetY;
    let nodeClicked = false;

    for (let n of nodes) {
        // 固定の15ではなく、そのノードの半径(n.size / 2)で当たり判定をする
        if (dist(mx, my, n.x, n.y) < n.size / 2) {
            draggedNode = n;
            energy = 1.0;
            nodeClicked = true;
            break;
        }
    }

    // ノード以外（背景）をクリックした場合は、全体スクロールを開始
    if (!nodeClicked) {
        isDraggingNetwork = true;
        dragStartX = mouseX - offsetX;
        dragStartY = mouseY - offsetY;
    }
}


function mouseDragged() {
    // ノードをドラッグしている場合
    if (draggedNode) {
        draggedNode.x = mouseX - offsetX;
        draggedNode.y = mouseY - offsetY;
        draggedNode.vx = 0;
        draggedNode.vy = 0;
        // energy = 1.0;
        if (energy < 0.2) energy = 0.2;
    }
    // 背景をドラッグしている場合（カメラの移動）
    else if (isDraggingNetwork) {
        offsetX = mouseX - dragStartX;
        offsetY = mouseY - dragStartY;
    }
}


function mouseReleased() {
    draggedNode = null;
    isDraggingNetwork = false; // 全体ドラッグの終了
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