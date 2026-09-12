"""Camera-free showcase using the project's actual detector and renderer."""
import argparse
import io
import json
import math
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cv2
import numpy as np
from src.tracker.base_detector import GreenBaseDetector
from src.hologram.renderer import HologramRenderer


def render_frame(angle=0, phase=0, show_detection=True):
    frame = np.full((540, 880, 3), (22, 18, 13), dtype=np.uint8)
    for x in range(0, 880, 40):
        cv2.line(frame, (x, 0), (x, 540), (34, 30, 24), 1)
    for y in range(0, 540, 40):
        cv2.line(frame, (0, y), (880, y), (34, 30, 24), 1)
    center = (440 + 90 * math.sin(phase / 20), 350)
    corners = cv2.boxPoints((center, (270, 55), angle)).astype(np.int32)
    cv2.fillConvexPoly(frame, corners, (70, 160, 75))
    detection, _ = GreenBaseDetector().detect(frame)
    if detection is None:
        raise RuntimeError('Synthetic base was not detected')
    frame = HologramRenderer().render(frame, detection['center'], detection['angle'], detection['size'], phase)
    if show_detection:
        cv2.polylines(frame, [corners], True, (180, 245, 220), 1, cv2.LINE_AA)
        cx, cy = map(int, detection['center'])
        cv2.drawMarker(frame, (cx, cy), (180, 245, 220), cv2.MARKER_CROSS, 16, 1)
    cv2.putText(frame, 'REAL DETECTOR / SYNTHETIC INPUT', (28, 36), cv2.FONT_HERSHEY_SIMPLEX, .5, (170, 190, 185), 1, cv2.LINE_AA)
    cv2.putText(frame, f"PCA orientation: {detection['angle']:+.1f} deg", (28, 505), cv2.FONT_HERSHEY_SIMPLEX, .55, (195, 225, 215), 1, cv2.LINE_AA)
    return frame, detection


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/':
            payload = Path(__file__).with_name('index.html').read_bytes()
            content_type = 'text/html; charset=utf-8'
        elif parsed.path == '/frame':
            values = parse_qs(parsed.query)
            try:
                angle = max(-55, min(55, float(values.get('angle', ['0'])[0])))
                phase = int(values.get('phase', ['0'])[0]) % 10000
                if not math.isfinite(angle): raise ValueError()
                frame, _ = render_frame(angle, phase, values.get('debug', ['1'])[0] == '1')
                ok, encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                if not ok: raise RuntimeError('Encoding failed')
                payload = encoded.tobytes()
                content_type = 'image/jpeg'
            except (ValueError, OverflowError):
                self.send_error(400, 'Invalid frame parameters')
                return
        elif parsed.path == '/health':
            payload = json.dumps({'status': 'ok', 'mode': 'synthetic-input-original-code'}).encode()
            content_type = 'application/json'
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *_):
        pass


def export():
    from PIL import Image
    destination = ROOT / 'docs'
    destination.mkdir(exist_ok=True)
    frames = []
    for step in range(32):
        frame, _ = render_frame(25 * math.sin(step * 2 * math.pi / 32), step)
        frames.append(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
    frames[0].save(destination / 'preview.png')
    frames[0].save(destination / 'preview.gif', save_all=True, append_images=frames[1:], duration=110, loop=0)
    print('Exported verified renderer preview')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--export', action='store_true')
    args = parser.parse_args()
    if args.export:
        export()
    else:
        print(f'Hologram demo: http://127.0.0.1:{args.port}', flush=True)
        ThreadingHTTPServer(('127.0.0.1', args.port), Handler).serve_forever()
