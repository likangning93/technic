class Beam {
  ArrayList<Joint> joints;
  float beam_length;
  Vec2 position = new Vec2(0.0, 0.0); // position of the end of the beam
  float rotation = 0.0; // CC rotation of the end of the beam
  int timestamp = 0;

  Beam(float beam_length) {
    this.beam_length = beam_length;
    joints = new ArrayList<Joint>();
  }
  
  Joint joinWithBeam(float joint_position, Beam other_beam, float other_position) {
    if (joint_position > beam_length || joint_position < 0.0) {
      print("error, joint position " + joint_position + " is not correct!");
      return null;
    }
    Joint new_joint = new Joint(this, other_beam, joint_position, other_position);
    this.joints.add(new_joint);
    other_beam.joints.add(new_joint);
    return new_joint;
  }
  
  Vec2 get_world_pos_along_line(float pos) {
    if (pos > beam_length || pos < 0.0) {
      println("error! position length is out of bounds!");
    }
    Vec2 zero_deg = new Vec2(pos, 0.0);
    return zero_deg.rotate(rotation).add(position);
  }
  
  Joint getSolvedJoint(int timestamp) {
    for (int i = 0; i < joints.size(); i++) {
      Joint j = joints.get(i);
      Beam b2 = j.b2;
      if (b2 == this) b2 = j.b1;
      if (b2.timestamp == timestamp) return j;
    }
    return null;
  }
  
  Joint getCommonJoint(Beam other) {
    for (int i = 0; i < joints.size(); i++) {
      Joint j1 = joints.get(i);
      for (int j = 0; j < other.joints.size(); j++) {
        Joint j2 = other.joints.get(j);
        if (j1 == j2) return j1;
      }
    }
    return null;
  }
}