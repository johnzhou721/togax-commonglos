# Usage

## Prerequisites

- Compile your Xcode project with an up-to-date SDK.  This means that you must hhave the latest updated SDK when you do ``briefcase run``.
- You want a MainWindow where the root structure is a tab bar (OptionContainer in Toga) and you have some scrollviews.  You'd like these scroll views to extend into unsafe area for iOS 26+ in order to produce Liquid Glass effects.
  - Same goes for WebViews.
- You need to check for iOS 26+ manually.
- You need to accept some imperfections, such as the scrollview being padded to the safe area horizontally (that is when you tilt your phone).  There's also where exceptions are raised every time you rotate your device; that is safe to ignore.

## API

```
OptionWindow([(content, tab text, icon, tab type), ...])
```
where if tab type is TabType.NORMAL or TabType.SCROLL, content is of instance toga.Widget; else if TabType is TabType.WEB, content is a tuple of a list and a dict as args and kwargs for WebView respectively.

Any TabType.SCROLL tabs' content will be vertically compressed to minimum height.

Any other options sent to toga.MainWindow is usable as well; however, note that specifying content will get ignored; things involving content generally should not be used.

```
create_webview_window(OPTIONS)
```

Returns a window with a WebView in it, with OPTIONS being the exact same args/kwargs you pass to WebView, passed the normal way.  The window will have top extended to create the fade effect.

```
ScrollMainWindow(OPTIONS)
```
Same API as MainWindow that puts its contents into a scroll view, using iOS26 fade effect.

The content to the window will be compressed to vertically minimum height. 
