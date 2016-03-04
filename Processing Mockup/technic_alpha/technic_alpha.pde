Solver technicSolver;
float driver_rotation = 0.0;
ArrayList<Beam> beams = new ArrayList<Beam>();
int timestamp = 0;
Joint driver;
float driveAngle = -0.8;

void setup() {
  Vec2 isx = circleIntersect(2.0, 3.0, 3.0, 1.0, -1.0, 4.0, 3.0, 1.0);
  println("isx test: " + isx.toString());
  ellipse(2.0, 3.0, 6.0, 6.0);
  ellipse(1.0, -1.0, 8.0, 8.0);
  ellipse(isx.x, isx.y, 2.0, 2.0);

  
  size(640, 480);
  Beam rootBeam = new Beam(100.0);
  rootBeam.position = new Vec2(320.0, 240.0);
  rootBeam.rotation = radians(90.0);
  technicSolver = new Solver(rootBeam);
  
  Beam secondBeam = new Beam(20.0);
  driver = rootBeam.joinWithBeam(40.0, secondBeam, 0.0);
  driver.isDriver = true;
  
  Beam thirdBeam = new Beam(60.0);
  thirdBeam.position = new Vec2(340.0, 178.0);
  thirdBeam.rotation = radians(90.0);
  thirdBeam.joinWithBeam(0.0, secondBeam, 20.0);
  
  Beam fourthBeam = new Beam(100.0);
  fourthBeam.position = new Vec2(320.0, 141.0);
  fourthBeam.rotation = radians(10.0);
  fourthBeam.joinWithBeam(0.0, rootBeam, 100.0);  
  
  fourthBeam.joinWithBeam(35.0, thirdBeam, 60.0);
  
  // initialize the machine
  beams.add(rootBeam);
  beams.add(secondBeam);
  beams.add(thirdBeam);
  beams.add(fourthBeam);
  //technicSolver.solve(timestamp);
  timestamp += 1;
  
  background(255);    
  driver.preferredAngle = driveAngle;
  technicSolver.solve(timestamp);
  for (int i = 0; i < beams.size(); i++) {
    drawBeam(beams.get(i));
  }  
  
}

void mouseClicked() {
    println("click at " + mouseX + " " + mouseY);
}

void draw() {

  if (keyPressed) {
    background(255);    
    timestamp++;
    driveAngle += 0.01;
    driver.preferredAngle = driveAngle;
    technicSolver.solve(timestamp);
    for (int i = 0; i < beams.size(); i++) {
      drawBeam(beams.get(i));
    }      
  }
}

void drawBeam(Beam drawMe) {
    // get position of the other end
    Vec2 otherEnd = new Vec2(drawMe.beam_length, 0.0); // processing's coordinate system is y down
    otherEnd = otherEnd.rotate(drawMe.rotation);
    otherEnd = otherEnd.add(drawMe.position);
    stroke(0.0, 0.0, 0.0);
    line(drawMe.position.x, drawMe.position.y, otherEnd.x, otherEnd.y);
    ellipse(drawMe.position.x, drawMe.position.y, 5, 5);
    
    
    for (int i = 0; i < drawMe.joints.size(); i++) {
      Joint joint = drawMe.joints.get(i);
      Vec2 jointPos = joint.getWorldPositionRelative(drawMe);
      stroke(255, 0.0, 0.0);
      ellipse(jointPos.x, jointPos.y, 4, 4);
    }
}