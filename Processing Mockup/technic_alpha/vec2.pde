class Vec2 {
  float x;
  float y;
  Vec2() {
  }
  
  Vec2(float x, float y) {
    this.x = x;
    this.y = y;
  }
  
  Vec2 add(Vec2 other) {
    return new Vec2(this.x + other.x, this.y + other.y);
  }
  
  Vec2 sub(Vec2 other) {
    return new Vec2(this.x - other.x, this.y - other.y);    
  }
  
  Vec2 rotate(float theta) {
    // a 2D rotation for CC is
    // | cos_theta -sin_theta | * [x]
    // | sin_theta  cos_theta |   [y]
    // but remember, processing's coordinate system is flipped!
    float cosTheta = (float) Math.cos(theta);
    float sinTheta = (float) Math.sin(theta);
    
    float new_x = this.x * cosTheta + this.y * sinTheta;
    float new_y = -this.x * sinTheta + this.y * cosTheta;
    return new Vec2(new_x, new_y);
  }
  
  String toString() {
    return this.x + " " + this.y;
  }
}