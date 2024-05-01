import importlib
import os
import openai
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.environ["OPENAI"]


def generate_cq_obj(user_msg: str):
    # Define the system message
    system_msg = """
    You are a strict assistant, translating natural language to CadQuery code. 
    Please do not explain, just write code. VERY IMPORTANT to name the output variable obj and do not use show_object or any show functions.

    You are not allowed to use triple backticks to indicate that the code is python.

    Here is the Cadquery API as a helpful resource:
 
    cq.Workplane.center(x, y)- Shift local coordinates to the specified location.
    cq.Workplane.lineTo(x, y[, forConstruction])- Make a line from the current point to the provided point
    cq.Workplane.line(xDist, yDist[, forConstruction])- Make a line from the current point to the provided point, using dimensions relative to the current point
    cq.Workplane.vLine(distance[, forConstruction])- Make a vertical line from the current point the provided distance
    cq.Workplane.vLineTo(yCoord[, forConstruction])- Make a vertical line from the current point to the provided y coordinate.
    cq.Workplane.hLine(distance[, forConstruction])- Make a horizontal line from the current point the provided distance
    cq.Workplane.hLineTo(xCoord[, forConstruction])- Make a horizontal line from the current point to the provided x coordinate.
    cq.Workplane.polarLine(distance, angle[, ...])- Make a line of the given length, at the given angle from the current point
    cq.Workplane.polarLineTo(distance, angle[, ...])- Make a line from the current point to the given polar coordinates
    cq.Workplane.moveTo([x, y])- Move to the specified point, without drawing.
    cq.Workplane.move([xDist, yDist])- Move the specified distance from the current point, without drawing.
    cq.Workplane.spline(listOfXYTuple[, tangents, ...])- Create a spline interpolated through the provided points (2D or 3D).
    cq.Workplane.parametricCurve(func[, N, start, ...])- Create a spline curve approximating the provided function.
    cq.Workplane.parametricSurface(func[, N, ...])- Create a spline surface approximating the provided function.
    cq.Workplane.threePointArc(point1, point2[, ...])- Draw an arc from the current point, through point1, and ending at point2
    cq.Workplane.sagittaArc(endPoint, sag[, ...])- Draw an arc from the current point to endPoint with an arc defined by the sag (sagitta).
    cq.Workplane.radiusArc(endPoint, radius[, ...])- Draw an arc from the current point to endPoint with an arc defined by the radius.
    cq.Workplane.tangentArcPoint(endpoint[, ...])- Draw an arc as a tangent from the end of the current edge to endpoint.
    cq.Workplane.mirrorY()- Mirror entities around the y axis of the workplane plane.
    cq.Workplane.mirrorX()- Mirror entities around the x axis of the workplane plane.
    cq.Workplane.wire([forConstruction])- Returns a CQ object with all pending edges connected into a wire.
    cq.Workplane.rect(xLen, yLen[, centered, ...])- Make a rectangle for each item on the stack.
    cq.Workplane.circle(radius[, forConstruction])- Make a circle for each item on the stack.
    cq.Workplane.ellipse(x_radius, y_radius[, ...])- Make an ellipse for each item on the stack.
    cq.Workplane.ellipseArc(x_radius, y_radius[, ...])- Draw an elliptical arc with x and y radiuses either with start point at current point or or current point being the center of the arc
    cq.Workplane.polyline(listOfXYTuple[, ...])- Create a polyline from a list of points
    cq.Workplane.close()- End construction, and attempt to build a closed wire.
    cq.Workplane.rarray(xSpacing, ySpacing, xCount, ...)- Creates an array of points and pushes them onto the stack.
    cq.Workplane.polarArray(radius, startAngle, ...)- Creates a polar array of points and pushes them onto the stack.
    cq.Workplane.slot2D(length, diameter[, angle])- Creates a rounded slot for each point on the stack.
    cq.Workplane.offset2D(d[, kind, forConstruction])- Creates a 2D offset wire.
    cq.Workplane.placeSketch(*sketches)- Place the provided sketch(es) based on the current items on the stack.
    cq.Workplane.gear(gear: BevelGear|CrossedHelicalGear|RackGear|RingGear|Worm)- Create a gear from the provided gear class.
    
    in the case of a parametric airfoil, write the code yourself to generate it. use Numpy for any math operation and dont forget to import it as a module
from math import cos, sin, radians, atan
import numpy as np
import cadquery as cq



def naca2130(x, c=1):
    m = 0.02
    p = 0.3
    t = 0.15

    yt = (t/0.2)*c*(0.2969*np.sqrt(x/c) - 0.1260*(x/c) - 0.3516*(x/c)**2 + 0.2843*(x/c)**3 - 0.1015*(x/c)**4)

    if x < p*c:
        yc = (m/p**2)*(2*p*(x/c) - (x/c)**2)
        theta = np.arctan((m/p**2)*(2*p - 2*(x/c)))
    else:
        yc = (m/(1-p)**2) * ((1 - 2*p) + 2*p*(x/c) - (x/c)**2)
        theta = np.arctan((m/(1-p)**2)*(2*p - 2*(x/c)))

    xu = x - yt*np.sin(theta)
    yu = yc + yt*np.cos(theta)
    xl = x + yt*np.sin(theta)
    yl = yc - yt*np.cos(theta)

    return xu, yu, xl, yl

def generate_airfoil_edge_points(N=100, c=1):
    x = np.linspace(0, c, N)
    uppers, lowers = [], []
    for xi in x:
        xu, yu, xl, yl = naca2130(xi, c)
        uppers.append((xu, yu))
        lowers.append((xl, yl))
    return uppers, lowers

def build_airfoil_wing(N=100, chord_length_root=1, taper_ratio=0.2, aspect_ratio=10):
    span = aspect_ratio * chord_length_root
    tip_chord_length = chord_length_root * taper_ratio

    # Generate edge points for the root airfoil
    root_uppers, root_lowers = generate_airfoil_edge_points(N, chord_length_root)
    root_profile = root_uppers + list(reversed(root_lowers))

    # Generate edge points for the tip airfoil, scaled by the taper ratio
    tip_uppers, tip_lowers = generate_airfoil_edge_points(N, tip_chord_length)
    tip_profile = tip_uppers + list(reversed(tip_lowers))

    # Construct the wing by lofting between the scaled root and tip profiles
    wing = (cq.Workplane("XY")
                .polyline(root_profile)
                .close()
                .workplane(offset=span, origin=(0, 0, span))  # Adjust origin for lofting to the tip profile. Do NOT use argument 'rotate' inside workplane() or the code will break!!!
                .polyline(tip_profile)
                .close()
                .loft())
    return wing

# Example usage
obj = build_airfoil_wing(N=100, chord_length_root=1, taper_ratio=0.2, aspect_ratio=10)

    REMEMBER: You are not allowed to use triple backticks to indicate that the code is python
    The code you are going to generate will be run directly in a pyython IDE, so your output needs to be executable code, dont include anything that could cause problems
    """

    system_msg2 = """you will receive an input that will consist of mission specification and requirements for a aircraft. your job is to take the information in that input and output a description that will be fed into an AI agent that will generate the cad model for the aircraft's wing. 
    based on the input, there is only 4 parameters you can vary:
    - NACA airfoil (only 4 digit)
    - aspect ratio
    - taper ratio
    - sweep angle

    here is an example of how your response should look like:

    "generate a CAD model of a wing using the NACA(insert 4 digit NACA serie) airfoil, with an aspect ratio of X, a taper ratio of X, and a sweep angle of X"


    Here's some general guidelines for decision making:
    - aircrafts with high mobility, like fighter jets, will have very low aspect ratio (1), very low taper ratio (0.1), high sweep angle.
    - aircrafts like gliders, will have a very high aspect ration and high taper ratio.
    - commercial aircrafts will have an high taper ratio, a moderate aspect ratio, and a moderate sweep angle
    - Remember, dont make the span


    Dont Include anything else in your response, since your output will be directly fed into the cad generation system. 
    """

    response2 = openai.ChatCompletion.create(
        model="gpt-4-0125-preview",
        messages=[
            {"role": "system", "content": system_msg2},
            {"role": "user", "content": user_msg},
        ],
    )
    
    print(response2)

    # Create a dataset using GPT
    response = openai.ChatCompletion.create(
        model="gpt-4-0125-preview",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": response2["choices"][0]["message"]["content"]},
        ],
    )

    current_datetime = datetime.now().isoformat()

    print(response)

    # create directory "generated" if does not exist
    if not os.path.exists("generated"):
        os.makedirs("generated")

    file_name = f"generated/{current_datetime}.py"
    with open(file_name, "w") as f:
        f.write(
            f'from math import cos, sin, radians, atan, tan\n{response["choices"][0]["message"]["content"]}'
        )

    try:
        print("1")
        spec = importlib.util.spec_from_file_location("obj_module", file_name)
        print("2")
        obj_module = importlib.util.module_from_spec(spec)
        print("3")
        spec.loader.exec_module(obj_module)
        print("final")
        return obj_module.obj
    except Exception as e:
        
        raise e

