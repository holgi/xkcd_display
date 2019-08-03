pillar_strength = 2;
pillar_height = 40;
pillar_width = 20;
hole_radius = 1.5;

module enforcement(size=10, strength=pillar_strength) {
    difference() {
        cube([strength, size,  size]);
        // diagonal cut
        translate([-strength / 2, size,  0]) 
            rotate([45, 0, 0]) 
            cube([strength*2, size*2, size*2]);
    }
}

module z_pillar(width=pillar_width, height=pillar_height, strength=pillar_strength, enforcement_size=10, hole_radius=hole_radius) {
    // Plate
    difference() {
        cube([width, width, strength]); 
        translate([width/2 + strength/2, width/2, -1])
            cylinder(h=strength+2, r=hole_radius, $fn=360);
        
    }
    // Wall
    cube([strength, width, height]);
    // enforcements
    translate([0, strength, 0]) 
        rotate([0, 0, 270]) 
        enforcement(enforcement_size);
    translate([0, width, 0]) 
        rotate([0, 0, 270]) 
        enforcement(enforcement_size);
    translate([strength, strength, height]) 
        rotate([180, 0, 270]) 
        enforcement(enforcement_size);
    translate([strength, width, height]) 
        rotate([180, 0, 270]) 
        enforcement(enforcement_size);
    
}

z_pillar(15);