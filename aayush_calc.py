import pygame
import pygame.gfxdraw

pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 800
MIN_PANEL_WIDTH, ZOOM_FACTOR = 200, 1.1
MIN_SCALE, MAX_SCALE, PAN_SPEED = 10, 500, 10
MAX_MOMENT, MAX_SHEAR = 107000, 300

WHITE, BLACK, RED, GREEN, GRAY, BLUE = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 255, 0), (200, 200, 200), (0, 0, 255)

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color, self.text, self.active = BLACK, text, False
        self.font = pygame.font.SysFont('Times New Roman', 24)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
        return False

    def draw(self, screen):
        txt_surface = self.font.render(self.text, True, self.color)
        self.rect.w = max(200, txt_surface.get_width() + 10)
        screen.blit(txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

def get_bounds(rectangles):
    if not rectangles:
        return -1, -1, 1, 1
    all_x = [coord for rect in rectangles for coord in [rect[0], rect[2]]]
    all_y = [coord for rect in rectangles for coord in [rect[1], rect[3]]]
    return min(all_x), min(all_y), max(all_x), max(all_y)

def calculate_centroid(rectangles):
    total_area, total_y = 0, 0
    for x1, y1, x2, y2 in rectangles:
        b, h = abs(x2 - x1), abs(y2 - y1)
        area, y_centroid = b * h, (y1 + y2) / 2
        total_area += area
        total_y += area * y_centroid
    return total_y / total_area if total_area else 0

def calculate_second_moment_of_area(rectangles, ybar):
    I_total = 0
    for x1, y1, x2, y2 in rectangles:
        b, h = abs(x2 - x1), abs(y2 - y1)
        area, y_centroid = b * h, (y1 + y2) / 2
        dy = y_centroid - ybar
        I_rect = (b * h**3) / 12
        I_total += I_rect + area * dy**2
    return I_total

def calculate_Q(rectangles, at_y):
    Q_total = 0
    for x1, y1, x2, y2 in rectangles:
        b_rect = abs(x2 - x1)
        if y2 > at_y:
            h = y2 - max(y1, at_y)
            area, y_centroid = b_rect * h, (at_y + y2) / 2
        elif y1 < at_y:
            h = min(at_y, y2) - y1
            area, y_centroid = b_rect * h, (y1 + min(at_y, y2)) / 2
        else:
            continue
        dy = abs(y_centroid - at_y)
        Q_total += area * dy
    return Q_total

def calculate_b(rectangles, at_y):
    return sum(abs(x2 - x1) for x1, y1, x2, y2 in rectangles if y1 <= at_y <= y2 or y2 <= at_y <= y1)

def calculate_tau(Q_total, I, b_total):
    return MAX_SHEAR * Q_total / (I * b_total) if I and b_total else 0

def find_ybar_I_tau(rectangles):
    ybar = calculate_centroid(rectangles)
    I = calculate_second_moment_of_area(rectangles, ybar)
    tau_centroid = calculate_tau(calculate_Q(rectangles, ybar), I, calculate_b(rectangles, ybar))
    tau_glue = calculate_tau(calculate_Q(rectangles, 75), I, calculate_b(rectangles, 75))
    return ybar, I, tau_centroid, tau_glue

def get_view(rectangles, screen_width, panel_width, screen_height):
    min_x, min_y, max_x, max_y = get_bounds(rectangles)
    margin = 20
    view_width, view_height = screen_width - panel_width - 2 * margin, screen_height - 2 * margin
    width_scale = view_width / (max_x - min_x) if max_x - min_x else float('inf')
    height_scale = view_height / (max_y - min_y) if max_y - min_y else float('inf')
    scale = max(MIN_SCALE, min(min(width_scale, height_scale) * 0.9, MAX_SCALE))
    center_x, center_y = (min_x + max_x) / 2, (min_y + max_y) / 2
    return scale, -center_x * scale, center_y * scale

def draw_ui(screen, input_boxes, add_button, undo_button, panel_width, screen_width, screen_height, ybar, I, tau_centroid, tau_glue, sigma_top, sigma_bottom):
    screen.fill(WHITE)
    pygame.draw.line(screen, BLACK, (panel_width, 0), (panel_width, screen_height))
    pygame.draw.rect(screen, GRAY, (panel_width - 2, 0, 4, screen_height))
    for box in input_boxes:
        box.draw(screen)
    pygame.draw.rect(screen, BLACK, add_button)
    screen.blit(pygame.font.SysFont('Times New Roman', 24).render("Add Rectangle", True, WHITE), (add_button.x + 10, add_button.y + 10))
    pygame.draw.rect(screen, BLACK, undo_button)
    screen.blit(pygame.font.SysFont('Times New Roman', 24).render("Undo", True, WHITE), (undo_button.x + 60, undo_button.y + 10))
    calc_value_font = pygame.font.SysFont('Times New Roman', 24)
    screen.blit(calc_value_font.render(f"I = {I:.2f}", True, BLACK), (20, 420))
    screen.blit(calc_value_font.render(f"ybar = {ybar:.2f}", True, BLACK), (20, 460))
    screen.blit(calc_value_font.render(f"tau_c = {tau_centroid:.2f}", True, BLACK), (20, 580))
    screen.blit(calc_value_font.render(f"tau_g = {tau_glue:.2f}", True, BLACK), (20, 620))
    screen.blit(calc_value_font.render(f"σ_top = {sigma_top:.2f}", True, BLACK), (20, 500))
    screen.blit(calc_value_font.render(f"σ_bottom = {sigma_bottom:.2f}", True, BLACK), (20, 540))

def draw_graph(screen, rectangles, panel_width, screen_width, screen_height, scale, pan_x, pan_y, ybar, sigma_top, sigma_bottom):
    origin_x, origin_y = panel_width + (screen_width - panel_width) // 2 + pan_x, screen_height // 2 + pan_y
    pygame.draw.line(screen, BLACK, (panel_width, origin_y), (screen_width, origin_y))
    pygame.draw.line(screen, BLACK, (origin_x, 0), (origin_x, screen_height))
    if rectangles:
        min_x, min_y, max_x, max_y = get_bounds(rectangles)
        y_top, y_bottom = max_y, min_y
        screen_y_top, screen_y_bottom = origin_y - y_top * scale, origin_y - y_bottom * scale
        pygame.draw.line(screen, BLUE, (panel_width, screen_y_top), (screen_width, screen_y_top), 2)
        pygame.draw.line(screen, BLUE, (panel_width, screen_y_bottom), (screen_width, screen_y_bottom), 2)
        graph_label_font = pygame.font.SysFont('Times New Roman', 16)
        screen.blit(graph_label_font.render(f"{sigma_top:.2f}", True, BLUE), (panel_width + 10, screen_y_top - 20))
        screen.blit(graph_label_font.render(f"{sigma_bottom:.2f}", True, BLUE), (panel_width + 10, screen_y_bottom + 5))
    for x1, y1, x2, y2 in rectangles:
        screen_x1, screen_y1 = origin_x + x1 * scale, origin_y - y1 * scale
        screen_x2, screen_y2 = origin_x + x2 * scale, origin_y - y2 * scale
        rect_left, rect_top = min(screen_x1, screen_x2), min(screen_y1, screen_y2)
        rect_width, rect_height = abs(screen_x2 - screen_x1), abs(screen_y2 - screen_y1)
        pygame.draw.rect(screen, RED, (rect_left, rect_top, rect_width, rect_height), 2)
        actual_width, actual_height = abs(x2 - x1), abs(y2 - y1)
        text_surface = graph_label_font.render(f"{actual_width:.1f} x {actual_height:.1f}", True, RED)
        screen.blit(text_surface, text_surface.get_rect(center=(rect_left + rect_width / 2, rect_top + rect_height / 2)))
    pygame.draw.line(screen, GREEN, (panel_width, origin_y - ybar * scale), (screen_width, origin_y - ybar * scale), 2)

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE | pygame.SCALED)
    pygame.display.set_caption('Rectangle Plotter')
    input_boxes = [InputBox(20, 100, 140, 32, '0,0'), InputBox(20, 200, 140, 32, '1,1')]
    add_button, undo_button = pygame.Rect(20, 300, 180, 40), pygame.Rect(20, 360, 180, 40)
    rectangles = [[0.0, 75.0, 100.0, 76.27], [10, 0, 11.27, 75], [88.73, 0, 90, 75], [11.27, 0, 88.73, 1.27], [11.27, 73.73, 16.27, 75], [83.73, 73.73, 88.73, 75]]
    panel_width, dragging_divider, scale, pan_x, pan_y = WINDOW_WIDTH // 2, False, 50, 0, 0
    ybar, I, sigma_top, sigma_bottom, tau_centroid, tau_glue = 0, 0, 0, 0, 0, 0
    running = True

    while running:
        screen_width, screen_height = screen.get_size()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE | pygame.SCALED)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if abs(event.pos[0] - panel_width) < 5:
                    dragging_divider = True
                elif add_button.collidepoint(event.pos):
                    try:
                        x1, y1 = map(float, input_boxes[0].text.split(','))
                        x2, y2 = map(float, input_boxes[1].text.split(','))
                        rectangles.append([x1, y1, x2, y2])
                        scale, pan_x, pan_y = get_view(rectangles, screen_width, panel_width, screen_height)
                        ybar, I, tau_centroid, tau_glue = find_ybar_I_tau(rectangles)
                    except:
                        pass
                elif undo_button.collidepoint(event.pos):
                    if rectangles:
                        rectangles.pop()
                        if rectangles:
                            scale, pan_x, pan_y = get_view(rectangles, screen_width, panel_width, screen_height)
                            ybar, I, tau_centroid, tau_glue = find_ybar_I_tau(rectangles)
                        else:
                            scale, pan_x, pan_y, ybar, I, sigma_top, sigma_bottom = 50, 0, 0, 0, 0, 0, 0
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging_divider = False
            elif event.type == pygame.MOUSEMOTION and dragging_divider:
                panel_width = max(MIN_PANEL_WIDTH, min(event.pos[0], screen_width - MIN_PANEL_WIDTH))
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]:
                    pan_y += PAN_SPEED if event.key == pygame.K_w else -PAN_SPEED if event.key == pygame.K_s else 0
                    pan_x += PAN_SPEED if event.key == pygame.K_a else -PAN_SPEED if event.key == pygame.K_d else 0
                elif event.key in [pygame.K_UP, pygame.K_DOWN]:
                    old_scale = scale
                    scale = scale / ZOOM_FACTOR if event.key == pygame.K_UP else max(scale / ZOOM_FACTOR, MIN_SCALE)
                    scale_factor = scale / old_scale
                    pan_x, pan_y = pan_x * scale_factor, pan_y * scale_factor
            for box in input_boxes:
                box.handle_event(event)

        draw_ui(screen, input_boxes, add_button, undo_button, panel_width, screen_width, screen_height, ybar, I, tau_centroid, tau_glue, sigma_top, sigma_bottom)
        draw_graph(screen, rectangles, panel_width, screen_width, screen_height, scale, pan_x, pan_y, ybar, sigma_top, sigma_bottom)
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()