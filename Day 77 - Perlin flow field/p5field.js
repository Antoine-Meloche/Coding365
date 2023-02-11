let inc, c, cols, rows, zOff;
let particles = [];
let flowField = [];

function setup() {
  createCanvas(500, 500);
  zOff = 0;
  c = 10;
  inc = 0.1;
  cols = floor(width / c);
  rows = floor(height / c);

  for (var i = 0; i < 2000; i++) {
    particles[i] = new Particle();
  }
  
  background(0);
}

function draw() {
  let yOff = 0;
  for (var y = 0; y < rows; y++) {
    let xoff = 0;
    
    for (var x = 0; x < cols; x++) {
      let index = (x + y * cols);
      let angle = noise(xoff, yOff, zOff) * TWO_PI;
      let vec = p5.Vector.fromAngle(angle);
      vec.setMag(1);
      flowField[index] = vec;
      xoff += inc;
    }
    
    yOff += inc;
    zOff += 0.0002;
  }

  for (var i = 0; i < particles.length; i++) {
    particles[i].update();
    particles[i].edges();
    particles[i].show();    
    particles[i].follow(flowField);
  }
}

function Particle() {
  this.pos = createVector(random(width), random(height));
  this.vel = createVector(0, 0);
  this.acc = createVector(0, 0);
  this.maxspeed = 1;

  this.prevPos = this.pos.copy();

  this.follow = function(vectors) {
    let x = floor(this.pos.x / c);
    let y = floor(this.pos.y / c);
    let index = x + y * cols;
    let force = vectors[index];
    this.applyForce(force);

  }

  this.update = function() {
    this.vel.add(this.acc);
    this.vel.limit(this.maxspeed);
    this.pos.add(this.vel);
    this.acc.mult(0);
  }

  this.applyForce = function(force) {
    this.acc.add(force);
  }

  this.show = function() {
    stroke(255, 3);
    strokeWeight(2);
    line(this.pos.x, this.pos.y, this.prevPos.x, this.prevPos.y);
    this.updatePrev();
  }

  this.updatePrev = function() {
    this.prevPos.x = this.pos.x;
    this.prevPos.y = this.pos.y;
  }
  this.edges = function() {
    if (this.pos.x > width) {
      this.pos.x = 0;
      this.updatePrev();
    }
    if (this.pos.x < 0) {
      this.pos.x = width;
      this.updatePrev();
    }
    if (this.pos.y > height) {
      this.pos.y = 0;
      this.updatePrev();
    }
    if (this.pos.y < 0) {
      this.pos.y = height;
      this.updatePrev();
    }
  }
}

