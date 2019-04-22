
using NUnit.Framework;
using System.IO;

namespace MockFailingTests
{
    [TestFixture]
    public class UnitTest1
    {
        /// <summary>
        /// Method uses a simple counter to simulate tests that sometimes fail.
        /// It stores a counter in a file so it is preserved between test reruns.
        /// Each test case specifies how many times it should fail before succeeding.
        /// </summary>
        /// <param name="fileName">Name of the file used for the counter. All files are in the temp path.</param>
        /// <param name="retries">How many times to fail before succeeding.</param>
        [TestCase("counter1.txt", 1)]
        [TestCase("counter2.txt", 2)]
        [TestCase("counter3.txt", 3)]
        public void FailUntil(string fileName, int retries)
        {
            fileName = $"{Path.GetTempPath()}/{fileName}";

            int counter = 0;
            if (File.Exists(fileName))
            {
                counter = int.Parse(File.ReadAllText(fileName));
            }

            counter++;
            File.WriteAllText(fileName, counter.ToString());

            if (counter % retries == 0 && File.Exists(fileName))
            {
                File.Delete(fileName);
            }

            Assert.AreEqual(0, counter % retries);
        }
    }
}
