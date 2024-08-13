

# Frogger

1. Start a new sketch with `draw`, `setup`, and `settings` methods. Ask your teacher if you do not know how to do this.

2.  In the `settings` method, set your canvas of size 800x600 for your game
size(width, height);
In the `draw` method, set the background color of your sketch
background(red,green,blue);
3. In the `draw` method, draw a frog on the bottom of the canvas. (It can be a ball for now)
fill(red, green, blue);
ellipse(x, y, width, height);
4. Make member variables to keep track of your frog’s hop distance, x and y position
5. Add code to the method below (match the code to the comments) to give our frog movement.
```
void keyPressed()
{
    if(key == CODED){
        if(keyCode == UP)
        {
            //Frog Y position goes up
        }
        else if(keyCode == DOWN)
        {
            //Frog Y position goes down 
        }
        else if(keyCode == RIGHT)
        {
            //Frog X position goes right
        }
        else if(keyCode == LEFT)
        {
            //Frog X position goes left
        }
    }
}
```
6. Write a method to keep our frog from going outside of the canvas
7. Create a new `Car` class in Eclipse. Your `Car` class will include the car’s x position, y position, the size of the car, and the speed of the car.
8. Create a constructor for your `Car` class that initializes each member variable with parameters.
9. Copy this functionality into your `Car` class to display your car
```
void display(PApplet applet)
  {
    fill(0,255,0);
    rect(x , y,  size, 50);
  }
```
10. Declare several `Car` member variables inside your `Frogger` class and initialize them in the setup method.
11. From your `draw` method, call each Car's `display` method like `car.display(this)`. You should see your cars appear.
    (note: passing the PApplet to the Car like this is an example of "inversion of control". That is, since a `Car` knows how to be a car, `Frogger` lets the `Car` be in charge of drawing the car).
12. Inside your Car class write a method for the car to move to the left with its speed.
13. Inside your Car class write a method for the car to move to the left with its speed. In the same method, if the car goes off the canvas, have it return to the rightmost position of your canvas.  (hint: use Processing's width variable)
14.  Write another method for the car to move to the right with its speed. In the same method,  if the car goes off the canvas, have it return to the leftmost position of your canvas
15.  In the draw() method, alternate the driving direction of each of your cars to either go left or right. Use the display() method after every drive method.
16. Create getX(), getY(), and getSize() methods in your Car class.
17. Check when a car hits your frog. You can use the following intersection method to help.
```
boolean intersects(Car car) {
 if ((frogY > car.getY() && frogY < car.getY()+50) &&
                (frogX > car.getX() && frogX < car.getX()+car.getSize())) {
   return true;
  }
 else  {
  return false;
 }
```
18. Call the intersects method for one of your cars in your draw method.  If the intersects method returns true, return your frog to the starting point.
19. Repeat step 18 for all of your cars.
20. OPTIONAL.   Use images for the background, cars and frog (see image at top). You can find your own images, or those provided in the Module 3 Java project. See below for code snippets to load and draw images.
```

 PImage back;
 PImage carLeft;
 PImage carRight;
 PImage frog;
    void settings(){
        size(844,600);
    }
    void setup() {
        back = loadImage("froggerBackground.png");
        carLeft = loadImage("carLeft.png");
        carLeft.resize(160,100);
        carRight = loadImage("carRight.png");
        carRight.resize(160,100);
        frog = loadImage("frog.png");
        frog.resize(75,75);
    }
    void draw() {
        background(back);
        image (carLeft,250,360);
        image (carRight,250, 210);
        image (frog, 300, 530);
    }
```


