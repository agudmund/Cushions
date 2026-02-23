using System.Diagnostics;

namespace Cushions; // Must match the project folder/namespace

public partial class MainPage : ContentPage
{
    public MainPage()
    {
        // This method links the XAML elements to these C# variables
        InitializeComponent();
    }

    private async void OnBrowseFileClicked(object sender, EventArgs e)
    {
        try
        {
            var result = await FilePicker.Default.PickAsync(new PickOptions
            {
                PickerTitle = "Select .md/.txt File",
                FileTypes = new FilePickerFileType(new Dictionary<DevicePlatform, IEnumerable<string>>
                {
                    { DevicePlatform.WinUI, new[] { ".txt", ".md" } },
                    { DevicePlatform.macOS, new[] { "txt", "md" } }
                })
            });

            if (result != null)
            {
                await ProcessFileAsync(result.FullPath);
            }
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"File picking failed: {ex.Message}");
        }
    }

    private async Task ProcessFileAsync(string path)
    {
        StatusLabel.Text = $"Processing {Path.GetFileName(path)}...";
        UploadProgress.IsVisible = true;
        UploadProgress.Progress = 0;

        try 
        {
            string content = await File.ReadAllTextAsync(path);
            var paragraphs = content.Split(new[] { "\n\n" }, StringSplitOptions.RemoveEmptyEntries);
            
            if (paragraphs.Length == 0)
            {
                StatusLabel.Text = "File is empty.";
                return;
            }

            for (int i = 0; i < paragraphs.Length; i++)
            {
                // Simulate Trello API delay
                await Task.Delay(600); 
                UploadProgress.Progress = (double)(i + 1) / paragraphs.Length;
            }

            StatusLabel.Text = $"Done! {paragraphs.Length} cards added.";
            
            // Updated to the non-obsolete method for .NET 10
            await this.DisplayAlertAsync("Success", "Board created with cards.", "OK");
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Critical failure: {ex.Message}");
            StatusLabel.Text = "Upload failed.";
        }
        finally
        {
            UploadProgress.IsVisible = false;
        }
    }

    private void OnShowLogClicked(object sender, EventArgs e) => Debug.WriteLine("Logs opened");
    private void OnShowFeaturesClicked(object sender, EventArgs e) => Debug.WriteLine("Features opened");
    private void OnSettingsClicked(object sender, EventArgs e) => Debug.WriteLine("Settings opened");
}
