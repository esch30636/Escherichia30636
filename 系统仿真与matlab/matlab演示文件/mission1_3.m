function mission1_3(str)
if nargin < 1
    disp('输入错误，请输入 sin, cos 或 tan');
    return;
end

x = 0:0.1:2*pi;

if strcmp(str, 'sin')
    plot(x, sin(x));
    title('y=sin(x)');
    ylim([-1.2, 1.2]);
elseif strcmp(str, 'cos')
    plot(x, cos(x));
    title('y=cos(x)');
    ylim([-1.2, 1.2]);
elseif strcmp(str, 'tan')
    y = tan(x);
    y(abs(y) > 10) = NaN;
    plot(x, y);
    title('y=tan(x)');
    ylim([-10, 10]);
else
    disp('输入错误，请输入 sin, cos 或 tan');
end

xlabel('x');
ylabel('y');
grid on;
end
