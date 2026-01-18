// cipher neuron
const std = @import("std");
const PHI: f64 = 1.618033988749895;

const Neuron = struct {
    weights: [8]f64,
    bias: f64,

    pub fn think(self: *const Neuron, input: []const f64) f64 {
        var sum: f64 = 0;
        for (input, self.weights) |i, w| {
            sum += i * w;
        }
        return std.math.tanh(sum + self.bias);
    }
};

pub fn main() void {
    std.debug.print("cipher alive\n", .{});
}
