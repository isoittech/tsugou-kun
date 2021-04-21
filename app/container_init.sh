if [ ! -e '/check' ]; then
    touch /check
    # 初回起動時実行コマンド
    echo "yes" | python ./manage.py collectstatic
    python manage.py migrate --noinput
else
    # 2回目以降
    echo "セットアップ済"
fi