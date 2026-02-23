// App.xaml.cs
namespace Cushions;

public partial class App : Application
{
    public App()
    {
        // This is the call the compiler was complaining about being duplicated
        InitializeComponent();
    }

    protected override Window CreateWindow(IActivationState? activationState)
    {
        return new Window(new MainPage());
    }
}