
height = 2;
servo_height = 3;

difference() {
    cylinder(h=height+servo_height, r=4, $fn=360);
    #translate([0, 0, height-1])
        cylinder(h=servo_height+2, r=3, $fn=6);
}
hull() {
    cylinder(h=height, r=6, $fn=360);
    translate([40,0,0])cylinder(h=height, r=2, $fn=360);
};
