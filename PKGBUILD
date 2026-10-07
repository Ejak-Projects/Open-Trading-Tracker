pkgname=open-trading-tracker
pkgver=1.0.0
pkgrel=1
pkgdesc="A modern, native portfolio and trading tracker"
arch=('any')
url="https://github.com/yourusername/open-trading-tracker"
license=('MIT')
depends=('python' 'pyside6' 'python-requests')
source=()

package() {
    cd "$startdir"

    # Install application python files
    install -d "$pkgdir/usr/share/$pkgname/app"
    cp -r app/* "$pkgdir/usr/share/$pkgname/app/"
    install -Dm644 main.py "$pkgdir/usr/share/$pkgname/main.py"

    # Install assets
    install -d "$pkgdir/usr/share/$pkgname/assets"
    install -Dm644 assets/icon.svg "$pkgdir/usr/share/$pkgname/assets/icon.svg"

    # Install launcher script
    install -Dm755 packaging/open-trading-tracker.sh "$pkgdir/usr/bin/open-trading-tracker"

    # Install desktop entry and system icon
    install -Dm644 packaging/open-trading-tracker.desktop "$pkgdir/usr/share/applications/open-trading-tracker.desktop"
    install -Dm644 assets/icon.svg "$pkgdir/usr/share/pixmaps/open-trading-tracker.svg"
}
