
from IPython.display import HTML
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

def animate_lips(lip_data, interval=150):
    n_frames = lip_data.shape[0]
    
    fig, ax = plt.subplots(figsize=(5, 5))
    
    all_x = lip_data[:, :, 0].flatten()
    all_y = lip_data[:, :, 1].flatten()
    margin = 0.1 * max(all_x.max() - all_x.min(), all_y.max() - all_y.min())
    ax.set_xlim(all_x.min() - margin, all_x.max() + margin)
    ax.set_ylim(all_y.min() - margin, all_y.max() + margin)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.invert_yaxis()  # т.к. координаты из видео идут сверху вниз
    
    line, = ax.plot([], [], 'o-', lw=2, markersize=5, color='crimson')
    title = ax.set_title("")
    
    def update(idx):
        pts = lip_data[idx]
        contour = np.vstack([pts, pts[0]])  # замыкаем контур
        line.set_data(contour[:, 0], contour[:, 1])
        title.set_text(f"Кадр {idx+1}/{n_frames}")
        return line, title
    
    ani = animation.FuncAnimation(fig, update, frames=n_frames,
                                  interval=interval, blit=True, repeat=True)
    plt.close(fig)  # важно! чтобы не было дублирующего статичного графика
    return HTML(ani.to_jshtml())
