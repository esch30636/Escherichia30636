x = linspace(0, 2*pi, 100);

plot(x, sin(x), 'r-', x, x, 'b--', x, tan(x), 'g-.');
legend('y=sin(x)', 'y=x', 'y=tan(x)');