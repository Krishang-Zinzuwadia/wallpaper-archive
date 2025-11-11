# Maintainer: Wallpaper Manager Team <maintainer@example.com>
pkgname=wallpaper-manager
pkgver=1.0.0
pkgrel=1
pkgdesc="A modern, transparent wallpaper manager for Arch Linux"
arch=('any')
url="https://github.com/user/wallpaper-manager"
license=('MIT')
depends=(
    'python>=3.11'
    'python-gobject'
    'gtk4'
    'python-pillow'
    'python-requests'
    'python-tomli-w'
    'python-xlib'
    'feh'
)
optdepends=(
    'swaybg: Wayland wallpaper support for Sway/Niri compositors'
    'nitrogen: Alternative X11 wallpaper backend'
)
makedepends=(
    'python-setuptools'
    'python-build'
    'python-installer'
    'python-wheel'
)
source=("$pkgname-$pkgver.tar.gz")
sha256sums=('SKIP')
install=$pkgname.install

build() {
    cd "$srcdir/$pkgname-$pkgver"
    python -m build --wheel --no-isolation
}

package() {
    cd "$srcdir/$pkgname-$pkgver"
    
    # Install Python package
    python -m installer --destdir="$pkgdir" dist/*.whl
    
    # Install systemd user service
    install -Dm644 wallpaper-manager-daemon.service \
        "$pkgdir/usr/lib/systemd/user/wallpaper-manager-daemon.service"
    
    # Install desktop entry
    install -Dm644 wallpaper-manager.desktop \
        "$pkgdir/usr/share/applications/wallpaper-manager.desktop"
    
    # Install documentation
    install -Dm644 README.md "$pkgdir/usr/share/doc/$pkgname/README.md"
    
    # Install license
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
