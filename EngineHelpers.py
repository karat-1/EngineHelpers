import pygame
import math


class Line:
    """
    Mathematicians will literally shit themselves in anger because this is not actually a line but a segment
    Dont forget to update your line coordinates via the update function before using its functions
    """

    @staticmethod
    def __calculate_orientation(p, q, r):
        val = (float(q.y - p.y) * (r.x - q.x)) - (float(q.x - p.x) * (r.y - q.y))
        if val > 0:
            return 1
        elif val < 0:
            return 2
        else:
            return 0

    @staticmethod
    def __onSegment(p, q, r):
        if ((q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and
                (q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))):
            return True
        return False

    @staticmethod
    def raycast(tile_map: dict, origin_position: pygame.Vector2, target_position: pygame.Vector2, tile_size: int, radius) -> pygame.Vector2:
        """
        Calculates the pixel position of where the line object intersects with the tiles on a tilemap
        E.g. if you want to test the line of sight you pass in the target_position of the enemy or the player as vector2
        If the function returns False, meaning your line does not collide with a rect, there is line of sight as no tiles obstruct the view
        :param origin_position: origin position from where we shoot the raycast
        :param tile_map: the tilemap as a dictionary with a tuple containing the x and y coordinates as keys: tile_map[(5,5)] = Tile()
        :param target_position: the x and y coordinates of target cell as a pygame.Vector2
        :param tile_size: the tile dimensions of the tile map. Only works with tiles where height == width
        :return: False if no collision or a pygame.Vector2 containing the exact point of collision
        """
        vec_intersection = 0

        target_cell = target_position / tile_size  # tile size
        vec_ray_start = origin_position / tile_size
        vec_ray_dir = (target_cell - vec_ray_start)
        vec_ray_dir = vec_ray_dir.normalize()

        try:
            vec_ray_stepsize = pygame.Vector2(math.sqrt(1 + (vec_ray_dir.y / vec_ray_dir.x) * (vec_ray_dir.y / vec_ray_dir.x)),
                                              math.sqrt(1 + (vec_ray_dir.x / vec_ray_dir.y) * (vec_ray_dir.x / vec_ray_dir.y)))
        except ZeroDivisionError:
            vec_ray_stepsize = pygame.Vector2(float('inf'), float('inf'))

        vec_map_check = pygame.Vector2(int(vec_ray_start.x), int(vec_ray_start.y))
        vec_ray_length_1d = pygame.Vector2()

        vec_step = pygame.Vector2()

        if vec_ray_dir.x < 0:
            vec_step.x = -1
            vec_ray_length_1d.x = (vec_ray_start.x - vec_map_check.x) * vec_ray_stepsize.x
        else:
            vec_step.x = 1
            vec_ray_length_1d.x = (vec_map_check.x + 1 - vec_ray_start.x) * vec_ray_stepsize.x

        if vec_ray_dir.y < 0:
            vec_step.y = -1
            vec_ray_length_1d.y = (vec_ray_start.y - vec_map_check.y) * vec_ray_stepsize.y
        else:
            vec_step.y = 1
            vec_ray_length_1d.y = (vec_map_check.y + 1 - vec_ray_start.y) * vec_ray_stepsize.y

        tile_found = False
        max_dist = radius / tile_size
        dist = 0
        while not tile_found and dist < max_dist:
            if vec_ray_length_1d.x < vec_ray_length_1d.y:
                vec_map_check.x += vec_step.x
                dist = vec_ray_length_1d.x
                vec_ray_length_1d.x += vec_ray_stepsize.x
            else:
                vec_map_check.y += vec_step.y
                dist = vec_ray_length_1d.y
                vec_ray_length_1d.y += vec_ray_stepsize.y
            if (int(vec_map_check.x), int(vec_map_check.y)) in tile_map:
                tile_found = True

        if tile_found:
            return vec_ray_start * tile_size + vec_ray_dir * tile_size * dist
            # return pygame.Vector2(round(vec_intersection.x), round(vec_intersection.y))

    @staticmethod
    def colliderect(rect: pygame.Rect) -> bool:
        """
        Checks if the line object collides with a given rectangle
        :param rect: rectangle of the object collisions should be checked with
        :return: True or False wether or not the line collides with given rectangle
        """
        edges = {'top': [pygame.Vector2(rect.topright), pygame.Vector2(rect.topleft)],
                 'bottom': [pygame.Vector2(rect.bottomright), pygame.Vector2(rect.bottomleft)],
                 'left': [pygame.Vector2(rect.topleft), pygame.Vector2(rect.bottomleft)],
                 'right': [pygame.Vector2(rect.topright), pygame.Vector2(rect.bottomright)]}

        for key in edges:
            if Line.collideline(edges[key][0], edges[key][1]):
                return True

    @staticmethod
    def collideline(origin_line_start: pygame.Vector2, origin_line_end: pygame.Vector2, sp_targetline: pygame.Vector2, ep_targetline: pygame.Vector2) -> bool:
        """
        Checks if the line object intersects with a given line
        :param origin_line_end: Endpoint of the origin line
        :param origin_line_start: Startpoint of the origin line
        :param sp_targetline: startpoint of the line we want to test collisions for
        :param ep_targetline: endpoint of the line we want to test collisions for
        :return: True if a collision happens, False if no Collision is detected
        """
        o1 = Line.__calculate_orientation(origin_line_start, origin_line_end, sp_targetline)
        o2 = Line.__calculate_orientation(origin_line_start, origin_line_end, ep_targetline)
        o3 = Line.__calculate_orientation(sp_targetline, ep_targetline, origin_line_start)
        o4 = Line.__calculate_orientation(sp_targetline, ep_targetline, origin_line_end)

        # General case
        if (o1 != o2) and (o3 != o4):
            return True

        # p1 , q1 and p2 are collinear and p2 lies on segment p1q1
        if (o1 == 0) and Line.__onSegment(origin_line_start, sp_targetline, origin_line_end):
            return True

        # p1 , q1 and q2 are collinear and q2 lies on segment p1q1
        if (o2 == 0) and Line.__onSegment(origin_line_start, ep_targetline, origin_line_end):
            return True

        # p2 , q2 and p1 are collinear and p1 lies on segment p2q2
        if (o3 == 0) and Line.__onSegment(sp_targetline, origin_line_start, ep_targetline):
            return True

        # p2 , q2 and q1 are collinear and q1 lies on segment p2q2
        if (o4 == 0) and Line.__onSegment(sp_targetline, origin_line_end, ep_targetline):
            return True

        # If none of the cases
        return False


class Collisionchecks:
    """
    A class including collisionschecks.
    """
    @staticmethod
    def point_in_circle(circle_origin: pygame.Vector2, radius: int, point_pos: pygame.Vector2) -> bool:
        """
        Collisionchecks for points inside a circle
        :param circle_origin: center origin position of the circle
        :param radius: radius of the circle
        :param point_pos: position of the point
        :return: True or False, whether the point is inside the circle or not
        """
        return (point_pos.x - circle_origin.x) ** 2 + (point_pos.y - circle_origin.y) ** 2 < radius ** 2

    @staticmethod
    def line_on_point(start: pygame.Vector2, end: pygame.Vector2, point: pygame.Vector2) -> bool:
        """
        Checks if a line intersects with a point
        :param start: startposition of the line
        :param end: endposition of the line
        :param point: position of the point
        :return: returns True if the point is on the line and False if it is not
        """
        d1 = math.dist((point.x, point.y), (start.x, start.y))
        d2 = math.dist((point.x, point.y), (end.x, end.y))

        line_len = math.dist((start.x, start.y), (end.x, end.y))
        buffer = 0.1
        return line_len - buffer <= d1 + d2 <= line_len + buffer

    @staticmethod
    def line_intersects_circle(circle_origin: pygame.Vector2, circle_radius: int, line_start: pygame.Vector2, line_end: pygame.Vector2) -> bool:
        """

        :param circle_origin: center position of the circle
        :param circle_radius: radius of the circle
        :param line_start: start position of line
        :param line_end:  endposition of line
        :return: Returns True if the line intersects with the circle or is inside the circle and False if it doesnt intersect or is not inside the circle
        """
        # check if the line is inside the circle
        start_inside = Collisionchecks.point_in_circle(circle_origin, circle_radius, line_start)
        end_inside = Collisionchecks.point_in_circle(circle_origin, circle_radius, line_end)
        if start_inside or end_inside:
            return True

        # length of the line
        dist_x = line_start.x - line_end.x
        dist_y = line_start.y - line_end.y
        line_length = math.sqrt((dist_x * dist_x) + (dist_y * dist_y))

        # dot product of line and circle
        dot = (((circle_origin.x - line_start.x) * (line_end.x - line_start.x)) + ((circle_origin.y - line_start.y) * (line_end.y - line_start.y))) / math.pow(line_length, 2)

        # closest point on line
        closest_x = line_start.x + (dot * (line_end.x - line_start.x))
        closest_y = line_start.y + (dot * (line_end.y - line_start.y))

        on_segment = Collisionchecks.line_on_point(line_start, line_end, pygame.Vector2(closest_x, closest_y))
        if not on_segment:
            return False

        dist_x = closest_x - circle_origin.x
        dist_y = closest_y - circle_origin.y
        distance = math.sqrt((dist_x * dist_x) + (dist_y * dist_y))

        return distance <= circle_radius


class Tile:
    """
    A basic tile class for prototyping pygame projects
    """
    def __init__(self, color, pos, rect=None):
        self.color = color
        self.rect = rect
        self.pos = pos  # as in cell position, not pixel position
        self.neighbours = []
        self.edges = {'N': False, 'S': False, 'W': False, 'E': False}
        self.edge_id = {}

    def reset_edges(self):
        self.edges = {'N': False, 'S': False, 'W': False, 'E': False}
        self.edge_id = {}

    def edge_exists(self, edge):
        return self.edges[edge]

    def set_edge(self, edge, edge_exists):
        self.edges[edge] = edge_exists

    def set_edge_id(self, edge, edge_id):
        self.edge_id[edge] = edge_id


class Edge:
    """
    A class holding data for lines, used for creating polyshapes
    """
    def __init__(self, sx, sy, ex, ey):
        self.start_x = sx
        self.start_y = sy
        self.end_x = ex
        self.end_y = ey
        self.color = (255, 0, 0)


class EngineMath:
    @staticmethod
    def GetTilesBetweenTwoPoints(x0, y0, x1, y1) -> list:
        """
        The Bresenham Line algorithm which will return a list of positions between 2 points in a grid
        This implementation works in all directions. This could potentially be used for continuous collision detection
        to get all tileposition on an axis
        :param x0: Start x of x0
        :param y0: Start y of y0
        :param x1: End x of x1
        :param y1: End y of y1
        :return: List of tuples which include (x, y) cell data in a grid
        """
        dx = x1 - x0
        dy = y1 - y0
        yn = y0
        xn = x0
        n = 0
        points = [(x0, y0)]

        if abs(dx) >= abs(dy):
            e1 = abs(dx) - 2 * abs(dy)
            while xn != x1:
                n += 1
                xn += EngineMath.sign(dx)
                if e1 > 0:
                    e1 = e1 - 2 * abs(dy)
                else:
                    yn += EngineMath.sign(dy)
                    e1 = e1 + 2 * (abs(dx) - abs(dy))
                points.append((xn, yn))
        else:
            e1 = abs(dy) - 2 * abs(dx)
            while yn != y1:
                n += 1
                yn += EngineMath.sign(dy)
                if e1 > 0:
                    e1 = e1 - 2 * abs(dx)
                else:
                    xn += EngineMath.sign(dx)
                    e1 = e1 + 2 * (abs(dy) - abs(dx))
                points.append((xn, yn))
        return points

    @staticmethod
    def sign(x: float) -> int:
        """
        Returns 1 if x is > 0 and -1 if x < 0 and 0 if x is 0
        :param x: value x
        :return: integer between 1 and -1
        """
        if x > 1:
            return 1
        elif x < 1:
            return -1
        return 0


class Loader:
    @staticmethod
    def load_img(path: str, colorkey=None, retain_alpha=True) -> pygame.Surface:
        """
        Loads an image
        :param path: Path to image
        :param colorkey: the color to key out
        :param retain_alpha: if alpha should be retained. If alpha is retained the performance will tank. Dont use it unless you need it.
        :return:
        """
        if retain_alpha:
            img = pygame.image.load(path).convert_alpha()
        else:
            img = pygame.image.load(path).convert()
        if colorkey:
            img.set_colorkey(colorkey)
        return img
