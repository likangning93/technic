class Joint {
  boolean isDriver;
  float preferredAngle; // preferred angle between these linked beams, if any
  Beam b1; // beams linked together by this joint
  Beam b2;
  float b1_pos; // position along b1's length
  float b2_pos; // position along b1's length

  Joint(Beam b1, Beam b2, float b1_pos, float b2_pos) {
    this.b1 = b1;
    this.b2 = b2;
    this.b1_pos = b1_pos;
    this.b2_pos = b2_pos;
    isDriver = false;
  }
  
  Vec2 getWorldPositionRelative(Beam b) {
    float alongBeam = 0.0;
    if (b == b1) alongBeam = b1_pos;
    if (b == b2) alongBeam = b2_pos;
    return b.get_world_pos_along_line(alongBeam);
  }
}