from django.shortcuts import render

import random
from django.shortcuts import render
from .models import GameScore


def index(request):
    # --- 1. 初期化・リセット ---
    if request.GET.get('move') == 'reset' or 'player_x' not in request.session:
        # プレイヤーの初期位置を 0〜4 の間でランダムに決定
        px = random.randint(0, 4)
        py = random.randint(0, 4)
        request.session['player_x'] = px
        request.session['player_y'] = py
        request.session['steps'] = 0
        request.session['msg'] = "スイカ割り開始！ボタンで移動してください。"
        request.session['is_cleared'] = False

        # スイカが「ランダムに決まったプレイヤーの位置」と重ならないように配置
        while True:
            sx, sy = random.randint(0, 4), random.randint(0, 4)
            if not (sx == px and sy == py):
                request.session['suika_x'], request.session['suika_y'] = sx, sy
                break

    # --- 2. 状態の読み込み ---
    px, py = request.session['player_x'], request.session['player_y']
    sx, sy = request.session['suika_x'], request.session['suika_y']
    steps = request.session['steps']
    is_cleared = request.session.get('is_cleared', False)

    # --- 3. 移動と距離計算 ---
    move = request.GET.get('move')
    if move and not is_cleared and move != 'reset':
        steps += 1
        if move == 'n' and py > 0:
            py -= 1
        elif move == 's' and py < 4:
            py += 1
        elif move == 'w' and px > 0:
            px -= 1
        elif move == 'e' and px < 4:
            px += 1

        # 距離の計算
        distance = abs(px - sx) + abs(py - sy)

        # --- 4. 当たり判定と【DBへの永続化】 ---
        if px == sx and py == sy:
            request.session['msg'] = f"🍉 おめでとう！{steps}歩でスイカを割りました！"
            is_cleared = True
            request.session['is_cleared'] = True

            # データベース(SQLite)にスコアを保存
            GameScore.objects.create(player_name="プレイヤー1", steps=steps)
        else:
            request.session['msg'] = f"移動しました。スイカまであと 【 {distance} 歩 】 です。"

    # --- 5. セッションの更新 ---
    request.session['player_x'], request.session['player_y'] = px, py
    request.session['steps'] = steps

    # --- 6. 盤面とランキングデータの作成 ---
    board = [["P" if x == px and y == py else "□" for x in range(5)] for y in range(5)]

    # DBから過去のクリア記録を最新5件取得
    recent_scores = GameScore.objects.order_by('-created_at')[:5]

    return render(request, 'suikagame/index.html', {
        'board': board,
        'msg': request.session['msg'],
        'steps': steps,
        'is_clear': is_cleared,
        'scores': recent_scores,
    })