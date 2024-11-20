import pygame

pygame.init()
WINDOW = pygame.display.set_mode((1200, 900))
pygame.display.set_caption("Cross-Section Calculator (PART BELOW THE CENTROIDAL AXIS MUST HAVE LEFT/RIGHT AND TOP/BOTTOM SYMMETRY)")
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SILVER = (192, 192, 192)
LIGHT_GRAY = (220, 220, 220)
DARK_GRAY = (128, 128, 128)
LIGHT_BLUE = (80, 196, 222)
ORANGE = (255, 99, 71)
RED = (255, 0, 0)
LIGHT_ORANGE = (255, 165, 0)
INPUT_FONT = pygame.font.SysFont("couriernew", 16, False)
INFORMATION_DISPLAY_FONT = pygame.font.SysFont("couriernew", 18, True)
OFFSET_X, OFFSET_Y = 550, 150

class InputBox:

    def __init__(self, x, y, description, width=150, height=25):
        self.x = x
        self.y = y
        self.colour = SILVER
        self.description = INPUT_FONT.render(description, 0, BLACK)
        self.width = width
        self.height = height
        self.active = False
        self.object = pygame.Rect(self.x, self.y, self.width, self.height)
        self.value = ""
    
    def set_validity(self, is_valid):
        if not is_valid:
            self.colour = RED
        else:
            self.colour = SILVER

    def draw(self):
        WINDOW.blit(self.description, (self.x, self.y - 25))
        pygame.draw.rect(WINDOW, self.colour, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(WINDOW, BLACK, (self.x, self.y, self.width, self.height), 1) # draws an outline
        text = INPUT_FONT.render(self.value, 0, BLACK)
        WINDOW.blit(text, (self.x + 2, self.y + (self.height // 2) - (text.get_height() // 2)))
    
    def behave(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.object.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.colour = LIGHT_GRAY if self.active else SILVER
        elif event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.value = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.value = self.value[:-1] # chop off last character
                else:
                    self.value += event.unicode

class Button:

    def __init__(self, x, y, description, width=125, height=40, colour=LIGHT_BLUE):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.description = INPUT_FONT.render(description, 0, BLACK)
        self.colour = colour
        self.object = pygame.Rect(self.x, self.y, self.width, self.height)
        self.clicked = False
    
    def draw(self):
        pygame.draw.rect(WINDOW, self.colour, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(WINDOW, BLACK, (self.x, self.y, self.width, self.height), 1) # draws an outline
        WINDOW.blit(self.description, (self.x + (self.width // 2) - (self.description.get_width() // 2), self.y + (self.height // 2) - (self.description.get_height() // 2)))

    def is_clicked(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.object.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                return True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        return False

class CrossSection:

    def __init__(self):
        self.x = 0
        self.y = 0
        self.components = []
        self.display_components = []
        self.global_min = 0
        self.second_moment_of_area = 0
        self.centroidal_axis = 0
        self.top_stress = 0
        self.bottom_stress = 0
        self.tensile_fos = 0
        self.compressive_fos = 0
        self.max_shear_stress = 0
        self.compressive_fos = 0
        self.tensile_fos = 0
        self.total_material_available = 813 * 1016 * 1.27 # mm^3
        self.material_used = 0
    
    def draw(self):
        for index, object in enumerate(self.display_components):
            pygame.draw.rect(WINDOW, DARK_GRAY, object)
            pygame.draw.rect(WINDOW, BLACK, object, 1)
            _, _, w, h = self.components[index][1]
            dimensions_text = INFORMATION_DISPLAY_FONT.render(f"{w} x {h}", 0, LIGHT_ORANGE)
            WINDOW.blit(dimensions_text, (object.centerx - (dimensions_text.get_width() // 2), object.centery - (dimensions_text.get_height() // 2)))
        centroidal_axis_display = INFORMATION_DISPLAY_FONT.render(f"y = {self.centroidal_axis} mm", 0, ORANGE)
        second_moment_of_area_display = INFORMATION_DISPLAY_FONT.render(f"I = {self.second_moment_of_area} mm^4", 0, ORANGE)
        top_stress_display = INFORMATION_DISPLAY_FONT.render(f"Top stress: {self.top_stress} MPa", 0, ORANGE)
        bottom_stress_display = INFORMATION_DISPLAY_FONT.render(f"Bottom stress: {self.bottom_stress} MPa", 0, ORANGE)
        shear_stress_display = INFORMATION_DISPLAY_FONT.render(f"Max shear: {self.max_shear_stress} MPa", 0, ORANGE)
        tensile_fos_display = INFORMATION_DISPLAY_FONT.render(f"Tensile FOS: {self.tensile_fos}", 0, ORANGE)
        compressive_fos_display = INFORMATION_DISPLAY_FONT.render(f"Compressive FOS: {self.compressive_fos}", 0, ORANGE)
        amount_materials_used = INFORMATION_DISPLAY_FONT.render(f"Materials used: {self.material_used} mm^3 / {self.total_material_available} mm^3", 0, ORANGE)
        WINDOW.blit(centroidal_axis_display, (70, 600))
        WINDOW.blit(second_moment_of_area_display, (70, 635))
        WINDOW.blit(top_stress_display, (70, 670))
        WINDOW.blit(bottom_stress_display, (70, 705))
        WINDOW.blit(tensile_fos_display, (70, 740))
        WINDOW.blit(compressive_fos_display, (70, 775))
        WINDOW.blit(shear_stress_display, (70, 805))
        WINDOW.blit(amount_materials_used, (70, 840))
    
    def get_first_moment_of_area_and_base_length(self):
        area, sum_area_y, base_length = 0, 0, 0
        q, base_length = 0, 0
        for object in self.components:
            _, y, w, h = object[1]
            if y + h > self.global_min - self.centroidal_axis:
                # area += w * min(h, self.centroidal_axis)
                # sum_area_y += w * min(h, self.centroidal_axis) * abs(max(self.global_min - self.centroidal_axis, y) + (min(h, self.centroidal_axis) / 2) - self.global_min)
                # q += w * min(h, self.centroidal_axis) * ((y + h - max(self.global_min - self.centroidal_axis, y)) // 2)
                centroidal_axis_from_top = self.global_min - self.centroidal_axis
                height = y + h - centroidal_axis_from_top if y < centroidal_axis_from_top else h
                local_centroidal_axis = y + (height / 2) if y > centroidal_axis_from_top else (centroidal_axis_from_top + (height / 2))
                dist = abs(local_centroidal_axis - centroidal_axis_from_top)
                q += w * height * dist
            if self.global_min - 1 <= y + h <= self.global_min + 1:
                base_length += w if y < (self.global_min - self.centroidal_axis) else 0
        # new_centroidal_axis = sum_area_y / area
        # print(f"New centroidal axis: {new_centroidal_axis}")
        # return (area * abs(self.centroidal_axis - new_centroidal_axis), base_length)
        print(f"First moment of area: {q}")
        return (q, base_length)
    
    def behave(self, event, moment, shear):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for index, object in enumerate(self.display_components):
                if object.collidepoint(event.pos):
                    self.display_components.pop(index)
                    self.components.pop(index)
                    break

        # find the y-coordinate of the global minimum (visually lowest, although technically it's the largest)
        self.global_min = 0
        for object in self.components:
            _, y, w, h = object[1]
            self.global_min = max(self.global_min, y + h)
        
        sum_area_y, sum_area = 0, 0
        for object in self.components:
            _, y, w, h = object[1]
            area = w * h
            local_y = abs(y + (h / 2) - self.global_min)
            sum_area += area
            sum_area_y += area * local_y
        if sum_area != 0:
            self.centroidal_axis = sum_area_y / sum_area
            self.material_used = sum_area * 1200 # mm^3
        else:
            self.centroidal_axis = 0
            self.material_used = 0
        # print(f"y: {self.centroidal_axis}, sum_area: {sum_area}, sum_area_y: {sum_area_y}")

        self.second_moment_of_area = 0
        for object in self.components:
            _, y, w, h = object[1]
            area = w * h
            self.second_moment_of_area += (area * (y + (h / 2) - (self.global_min - self.centroidal_axis)) ** 2) + (w * (h ** 3)) / 12
        # print(f"I: {self.second_moment_of_area}")

        if moment:
            try:
                float(moment) # if this fails, it will be caught by the exception block
                self.top_stress = abs(float(moment)) * (self.global_min - self.centroidal_axis) / self.second_moment_of_area
                self.bottom_stress = abs(float(moment)) * self.centroidal_axis / self.second_moment_of_area
                if float(moment) > 0: # top is in compression
                    self.top_stress *= -1
                else:
                    self.bottom_stress *= -1
                if self.top_stress < 0: # top compression
                    self.compressive_fos = 6 / abs(self.top_stress)
                    self.tensile_fos = 30 / abs(self.bottom_stress)
                elif self.top_stress > 0: # top tension
                    self.compressive_fos = 6 / abs(self.bottom_stress)
                    self.tensile_fos = 30 / abs(self.top_stress)
                else:
                    self.compressive_fos, self.tensile_fos = 0, 0
            except Exception as e:
                print(f"Moment: {e}")
                moment_box.set_validity(False)
        else:
            self.top_stress, self.bottom_stress = 0, 0
        
        if shear:
            try:
                float(shear)
                q, b = self.get_first_moment_of_area_and_base_length()
                print(q)
                self.max_shear_stress = (float(shear) * q) / (self.second_moment_of_area * b)
                print(self.max_shear_stress)
            except Exception as e:
                print(f"Shear: {e}")
                shear_force_box.set_validity(False)
        else:
            self.max_shear_stress = 0

x_box = InputBox(70, 100, "Input the x coordinate (top left): ")
y_box = InputBox(70, 175, "Input the y coordinate (top left): ")
width_box = InputBox(70, 250, "Input the width: ")
height_box = InputBox(70, 325, "Input the height: ")
moment_box = InputBox(70, 475, "Input the max moment (negative for top tension): ")
shear_force_box = InputBox(70, 550, "Input the max shear: ")
input_fields = [x_box, y_box, width_box, height_box, moment_box, shear_force_box]
add_object_button = Button(70, 385, "Add")

cross_section = CrossSection()

def overlaps(coords1, coords2) -> bool:
    x1, y1, w1, h1 = coords1
    x2, y2, w2, h2 = coords2
    left1, right1 = x1, x1 + w1
    top1, bottom1 = y1, y1 + h1
    left2, right2 = x2, x2 + w2
    top2, bottom2 = y2, y2 + h2

    return not (
        right1 <= left2 or
        left1 >= right2 or
        bottom1 <= top2 or
        top1 >= bottom2
    )

def draw_background() -> None:
    WINDOW.fill(WHITE)

def draw_elements() -> None:
    draw_background()
    for field in input_fields:
        field.draw()
    add_object_button.draw()
    cross_section.draw()

def behave_elements(event, moment, shear) -> None:
    for field in input_fields:
        field.behave(event)
    cross_section.behave(event, moment, shear)

def main() -> None:
    clock = pygame.time.Clock()
    run = True

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            behave_elements(event, moment_box.value, shear_force_box.value)

        if add_object_button.is_clicked():
            try:
                for index, field in enumerate(input_fields):
                    if index < len(input_fields) - 2:
                        float(field.value)      # check if it's a float. If not, it will go to the exception block

                # create a new rectangle with an offset to the coordinate
                new_rectangle = pygame.Rect(OFFSET_X + float(x_box.value), OFFSET_Y + float(y_box.value), float(width_box.value), float(height_box.value))
                display_rectangle = pygame.Rect(OFFSET_X + 5 * float(x_box.value), OFFSET_Y + 5 * float(y_box.value), 5 * float(width_box.value), 5 * float(height_box.value))
                for object in cross_section.components:
                    if overlaps((OFFSET_X + float(x_box.value), OFFSET_Y + float(y_box.value), float(width_box.value), float(height_box.value)), object[1]): # check if it's overlapping with other objects which is bad
                        for field in input_fields:
                            field.set_validity(False)
                        break
                else:
                    cross_section.components.append((new_rectangle, (float(x_box.value), float(y_box.value), float(width_box.value), float(height_box.value))))
                    cross_section.display_components.append(display_rectangle)
                    for index, field in enumerate(input_fields):
                        if index == 4:
                            break
                        field.value = ""
            except Exception as e:
                for field in input_fields:
                    field.set_validity(False)
                print(e)

        draw_elements()

        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
