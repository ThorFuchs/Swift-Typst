//! Compare the existing f32 degree-elevation formula with kurbo's public API.
//! This does not implement or relicense krilla's attributed path method.
use kurbo::QuadBez;

fn original(a: f32, b: f32) -> f32 { (a + b * 2.0) / 3.0 }

fn main() {
    let mut state: u32 = 0x5234_9876;
    let mut next = || {
        state = state.wrapping_mul(1_664_525).wrapping_add(1_013_904_223);
        (state % 20_000_001) as f32 / 1000.0 - 10_000.0
    };
    let mut differing = 0usize;
    let mut max_abs = 0.0f32;
    let samples = 100_000;
    for _ in 0..samples {
        let (a, b, c) = (next(), next(), next());
        let raised = QuadBez::new((a as f64, 0.0), (b as f64, 0.0), (c as f64, 0.0)).raise();
        for (old, new) in [(original(a, b), raised.p1.x as f32), (original(c, b), raised.p2.x as f32)] {
            if old.to_bits() != new.to_bits() { differing += 1; }
            max_abs = max_abs.max((old - new).abs());
        }
        assert_eq!(raised.p0.x as f32, a);
        assert_eq!(raised.p3.x as f32, c);
    }
    assert!(max_abs < 0.005, "unexpected error at sampled coordinate scale");
    println!("samples={samples} controls={} bitwise_different={differing} max_abs={max_abs:.9}", samples * 2);
    println!("This measures numeric controls only; PDF paths and rights still require separate review.");
}
