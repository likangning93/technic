class Solver {
  Beam root;
  
  Solver(Beam root) {
    this.root = root;
  }
  
  void solve(int timestamp) {
    recursive_solve(root, timestamp);
    return;
  }
  
  void recursive_solve(Beam b1, int timestamp) {
    // if the b1 is already up-to-date, return
    if (b1.timestamp == timestamp) return;
    // update b1's timestamp, marking it as up-to-date
    b1.timestamp = timestamp;
    // for each joint in b1:
    for (int i = 0; i < b1.joints.size(); i++) {
      Joint joint = b1.joints.get(i);
      Beam b2 = joint.b2;
      if (b2 == b1) {
        b2 = joint.b1;
      }
      
      
      // if the linked beam is up-to-date by timestamp, continue
      if (b2.timestamp == timestamp) continue;
      // if the joint has a preferred angle:
      if (joint.isDriver) {
        setAnglePosition(joint, joint.preferredAngle, b1, b2);
        // mark b2 as up-to-date
        b2.timestamp = timestamp;
        continue;
      }
            
      
      // otherwise, assume this link is part of a kinematic chain.
      ArrayList<Beam> quad = new ArrayList<Beam>();
      ArrayList<Joint> joints = new ArrayList<Joint>();
      if (!checkQuad(b1, joint, quad, joints)) {
        print("ERROR beams do not form a quad!");
        return;
      }
      
      Beam unsolved1 = null;
      Beam unsolved2 = null;

      // figure out which beams in the quad are unsolved
      for (int j = 0; j < 4; j++) {
        Joint currJoint = joints.get(j);
        Beam currBeam = quad.get(j);
        //println(currBeam.position.toString() + " " + currBeam.timestamp);
        
        // if a non-up-to-date beam is linked to this with a joint that has a preferred angle,
        // update that beam first as above.
        if (currBeam.timestamp < timestamp && currJoint.isDriver) {
          currBeam.timestamp = timestamp;
          setAnglePosition(currJoint, currJoint.preferredAngle, root, currBeam);
          continue;
        }
        if (currBeam.timestamp < timestamp) {
          if (unsolved1 == null) unsolved1 = currBeam;
          else unsolved2 = currBeam;
        }
      }
      if (unsolved2 == null) {
        //println("not enough unsolved?");
        return;
      }
      // correct the two unsolved beams' positions
      Joint unsolved1ToSolved = unsolved1.getSolvedJoint(timestamp);
      Beam solvedBeam1 =unsolved1ToSolved.b2;
      if (solvedBeam1 == unsolved1) solvedBeam1 = unsolved1ToSolved.b1;
      setAnglePosition(unsolved1ToSolved, 0.0, solvedBeam1, unsolved1);
      
      Joint unsolved2ToSolved = unsolved2.getSolvedJoint(timestamp);
      Beam solvedBeam2 =unsolved2ToSolved.b2;
      if (solvedBeam2 == unsolved2) solvedBeam1 = unsolved2ToSolved.b1;
      setAnglePosition(unsolved2ToSolved, 0.0, solvedBeam2, unsolved2);      
      
      // perform the circle solve to correct the two unsolved beams' orientations
      // http://math.stackexchange.com/questions/256100/how-can-i-find-the-points-at-which-two-circles-intersect
      // better version here: http://paulbourke.net/geometry/circlesphere/
      
      Vec2 p1 = unsolved1ToSolved.getWorldPositionRelative(solvedBeam1);
      Vec2 p2 = unsolved2ToSolved.getWorldPositionRelative(solvedBeam2);     
      
      Joint shared = unsolved1.getCommonJoint(unsolved2);
      Vec2 pCurr2 = shared.getWorldPositionRelative(unsolved2);
      Vec2 pCurr1 = shared.getWorldPositionRelative(unsolved1);
      
      //println((shared.b1 == unsolved1 || shared.b2 == unsolved1) + " " + (shared.b1 == unsolved2 || shared.b2 == unsolved2));
      
      float r1 = shared.b1_pos;
      if (shared.b2 == solvedBeam1) r1 = unsolved1ToSolved.b2_pos;
      
      float r2 = shared.b2_pos;
      if (shared.b1 == solvedBeam1) r2 = unsolved1ToSolved.b1_pos;
      
      Vec2 solvedPoint = circleIntersect(p1.x, p1.y, r1, p2.x, p2.y, r2, pCurr2.x, pCurr2.y);
      
      //println("p1 is " + p1.toString() + " radius is " + r1);
      //println("p2 is " + p2.toString() + " radius is " + r2);
      //println("pCurr2 is " + pCurr2.toString());
      //println("pCurr1 is " + pCurr1.toString());
      
      //println("solved point is " + solvedPoint.toString());
      
      // compute corrected orientations for the two unsolved beams
      Vec2 orient1 = solvedPoint.sub(p1);
      Vec2 orient2 = solvedPoint.sub(p2);
      
      float angle1 = angleToPosition(orient1.x, orient1.y);
      float angle2 = angleToPosition(orient2.x, orient2.y);
      unsolved1.rotation = angle1;
      unsolved2.rotation = angle2;
      
      //println("angle for 1 is: " + angle1);
      //println("angle for 2 is: " + angle2);
      //println();
      
      noFill();
      stroke(0, 255, 0);
      ellipse(p1.x, p1.y, 4, 4);
      ellipse(p1.x, p1.y, r1 * 2.0, r1 * 2.0);
      stroke(0, 0, 255);
      ellipse(p2.x, p2.y, 4, 4);
      ellipse(p2.x, p2.y, r2 * 2.0, r2 * 2.0);      
      stroke(0, 255, 255);
      ellipse(solvedPoint.x, solvedPoint.y, 8, 8);
      
      // recurse on the unsolved beams
      recursive_solve(unsolved1, timestamp);
      recursive_solve(unsolved2, timestamp);      
    }
    return;
  }
  
  void setAnglePosition(Joint j, float angle, Beam fixed, Beam update) {
      update.rotation = fixed.rotation + angle;
      // translate b2 so it is attached to b1 by the joint position
      Vec2 fixedJointWorld = j.getWorldPositionRelative(fixed);
      Vec2 updateJointWorld = j.getWorldPositionRelative(update);
      Vec2 displaceBy = fixedJointWorld.sub(updateJointWorld);
      update.position = update.position.add(displaceBy);
      return;
  }
  
  boolean checkQuad(Beam b1, Joint j1, ArrayList<Beam> quad, ArrayList<Joint> joints) {
    // check if the beam at the other end of joint j links back to b1 to form a quad.
    // j1 links b1 to b2.
    Beam b2 = j1.b2;
    if (b2 == b1) {
      b2 = j1.b1;
    }
    // since we know we want a quad we can do this with a nested FOR
    for (int i2 = 0; i2 < b2.joints.size(); i2++) {
      // check each of b2's links
      Joint j2 = b2.joints.get(i2);
      if (j2 == j1) continue;
      Beam b3 = j2.b2;
      if (b3 == b2) {
        b3 = j2.b1;
      }
      for (int i3 = 0; i3 < b3.joints.size(); i3++) {
        Joint j3 = b3.joints.get(i3);
        if (j3 == j2) continue;
        Beam b4 = j3.b2;
        if (b4 == b3) {
          b4 = j3.b1;
        }
        for (int i4 = 0; i4 < b4.joints.size(); i4++) {
          Joint j4 = b4.joints.get(i4);
          if (j4 == j3) continue;
          Beam b5 = j4.b2;
          if (b5 == b4) {
            b5 = j4.b1;
          }
          if (b5 == b1) {
            joints.add(j1);
            joints.add(j2);
            joints.add(j3);
            joints.add(j4);
            quad.add(b1);
            quad.add(b2);
            quad.add(b3);
            quad.add(b4);
            return true;
          }
        }
      }
    }
    return false;
  }
}

float quadratic(float a, float b, float c, boolean pos) {
  float plusMinus = -1.0;
  if (pos) plusMinus = 1.0;
  return (-b + plusMinus * sqrt(b * b - 4.0 * a * c)) / (2.0 * a);
}

Vec2 circleIntersect(float p0_x, float p0_y, float r0, float p1_x, float p1_y, float r1, float curr_x, float curr_y) {
  // http://paulbourke.net/geometry/circlesphere/
  // distance d between circle centers
  float d_x = p0_x - p1_x;
  float d_y = p0_y - p1_y;
  float d = sqrt(d_x * d_x + d_y * d_y);
  if (d > r0 + r1) return null; // circles separate
  if (d < abs(r0 - r1)) return null; // one circle fully inside other
  
  float a = (r0 * r0 - r1 * r1 + d * d) / (2.0 * d);
  float h = sqrt(r0 * r0 - a * a);
  
  float p2_x = p0_x + a * (p1_x - p0_x) / d;
  float p2_y = p0_y + a * (p1_y - p0_y) / d;
  
  float p3_1x = p2_x + h * (p1_y - p0_y) / d;
  float p3_1y = p2_y - h * (p1_x - p0_x) / d;
  
  float p3_2x = p2_x - h * (p1_y - p0_y) / d;
  float p3_2y = p2_y + h * (p1_x - p0_x) / d;
  
  float dist_1_x = p3_1x - curr_x;
  float dist_1_y = p3_1y - curr_y;
  
  float dist_2_x = p3_2x - curr_x;
  float dist_2_y = p3_2y - curr_y;  
  
   println("got positions: " + p3_1x + " " + p3_1y + " and " + p3_2x + " " + p3_2y);
   println("comparing to: " + curr_x + " " + curr_y);
   println();  
  
   stroke(255, 0, 255);
   ellipse(curr_x, curr_y, 4, 4);
  
   if (dist_2_x * dist_2_x + dist_2_y * dist_2_y > dist_1_x * dist_1_x + dist_1_y * dist_1_y) {
    return new Vec2(p3_1x, p3_1y);
  }
  else return new Vec2(p3_2x, p3_2y);
  
  /* derived straight from the formulas. seems to have numerical error problems
  float z1 = (r1 * r1 - r2 * r2) - (x1 * x1 - x2 * x2) - (y1 * y1 - y2 * y2);
  float z2 = -2.0 * (y1 - y2);
  float z3 = 2.0 * (x1 - x2);
  float a = z2 * z2 + z3 * z3;
  float b = -2.0 * x1 * z2 * z2 + 2.0 * z1 * z3 - 2.0 * z2 * z3 * y1;
  float c = z2 * z2 * x1 * x1 + z1 * z1 - 2.0 * z1 * z2 * y1 + y1 * y1 - r1 * r1;
  
  float x_solve_1 = quadratic(a, b, c, true);
  float y_solve_1 = (z1 + z3 * x_solve_1) / z2;
  
  float x_solve_2 = quadratic(a, b, c, false);
  float y_solve_2 = (z1 + z3 * x_solve_2) / z2;
  
  float dist_1_x = x_solve_1 - curr_x;
  float dist_1_y = y_solve_1 - curr_y;
  
  float dist_2_x = x_solve_2 - curr_x;
  float dist_2_y = y_solve_2 - curr_y;
  
  if (dist_2_x * dist_2_x + dist_2_y * dist_2_y < dist_1_x * dist_1_x + dist_1_y * dist_1_y) {
    return new Vec2(x_solve_2, y_solve_2);
  }
  else return new Vec2(x_solve_1, y_solve_1); */
}

float angleToPosition(float x, float y) {
  // return the angle relative to horizontal needed to achieve the
  // given vector orientation
  // normalize vector. dot product is just xn since horizontal vector is (1, 0)
  // cos(theta) = dot(a, b)
  float length = sqrt(x * x + y * y);
  float dot = x / length;
  return acos(dot);
}