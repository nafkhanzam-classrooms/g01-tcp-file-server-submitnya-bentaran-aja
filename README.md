[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/mRmkZGKe)
# Network Programming - Assignment G01

## Anggota Kelompok
| Nama           | NRP        | Kelas     |
| ---            | ---        | ----------|
| Yasmina Fitri Azizah               | 5025241039           | Pemrograman Jaringan D           |
| Kinanti Ayu Caesandria               | 5025241047           | Pemrograman Jaringan D           |

## Link Youtube (Unlisted)
Link ditaruh di bawah ini
```
https://youtu.be/CR7GJ43hu6Y
```

## Penjelasan Program
### Deskripsi Umum
Program ini merupakan implementasi komunikasi client-server menggunakan socket TCP. Sistem mendukung:

* Multiple client
* File upload & download
* List file pada server
* Broadcast message antar client


# Client

## Mekanisme!

Client menggunakan:

* **1 thread utama** → input user
* **1 listener thread** → menerima data dari server

Komunikasi dilakukan dengan format:

* `/list`
* `/upload <filename>`
* `/download <filename>`
* pesan biasa/broadcast

Fitur: Menggunakan **queue** untuk sinkronisasi upload & download dan menggunakan **delimiter `\n`** untuk parsing pesan.

# Server Sync (Synchronous)

##  Mekanisme

Server bekerja secara **blocking (synchronous)**:

* Hanya melayani **1 client dalam satu waktu**
* Client lain harus menunggu hingga koneksi selesai

Alur kerja:

1. Server menerima koneksi
2. Memproses semua request client
3. Setelah selesai, baru menerima client berikutnya

# Server Thread (Multithreading)

##  Mekanisme

Setiap client ditangani oleh **thread terpisah**:

* 1 client = 1 thread
* Semua client dapat berjalan secara paralel

Alur kerja:

1. Server menerima koneksi
2. Membuat thread baru untuk client
3. Thread menangani komunikasi client secara independen

# Server Select (I/O Multiplexing)

## Mekanisme

Server menggunakan **select()**:

* Hanya **1 thread**
* Mengawasi banyak socket sekaligus

Alur kerja:

1. Server memonitor semua socket
2. Jika ada socket aktif → diproses
3. Loop terus untuk semua client

# Server Poll (I/O Multiplexing)

Server menggunakan **poll()**:
* Hanya **1 thread**
* Mengawasi banyak socket sekaligus

Alur kerja:

1. Setiap client disimpan sebagai file descriptor (fd)
2. Server memonitor semua socket
3. Jika ada socket aktif, maka client akan diproses satu per satu
4. Di-loop terus menerus untuk semua client

## Screenshot Hasil

### Server Sync

* Server Side
  
  <img width="335" height="213" alt="Screenshot 2026-03-25 193331" src="https://github.com/user-attachments/assets/9cde4baa-81fd-4cde-baa7-c228c9eeebd1" />

* Client 1
  
  <img width="596" height="283" alt="Screenshot 2026-03-25 193435" src="https://github.com/user-attachments/assets/9da35b8a-ef7d-4264-aaae-82662cef8a44" />

* Client 2
  
  <img width="583" height="211" alt="Screenshot 2026-03-25 193506" src="https://github.com/user-attachments/assets/2d1495cd-8039-4201-838e-9d730cf4d86e" />
  

### Server Thread

* Server Side
  
  <img width="607" height="358" alt="Screenshot 2026-03-25 200704" src="https://github.com/user-attachments/assets/39fd5d75-758f-4167-9b45-fd5286548f3d" />

* Client 1
  
  <img width="641" height="473" alt="Screenshot 2026-03-25 200718" src="https://github.com/user-attachments/assets/12f08f36-f48a-4edc-912b-de64c9b6c9fe" />

* Client 2
  
  <img width="755" height="440" alt="Screenshot 2026-03-25 200729" src="https://github.com/user-attachments/assets/8d2c2706-01ea-42e7-bd26-96bca9633804" />

* Client 3
  
  <img width="537" height="373" alt="Screenshot 2026-03-25 200739" src="https://github.com/user-attachments/assets/da12eac9-6761-486f-9675-0d32e1860139" />


### Server Select

* Server Side
  
  <img width="612" height="370" alt="Screenshot 2026-03-25 194009" src="https://github.com/user-attachments/assets/2c8c552d-051a-41ad-97b5-1f8aedc3de7c" />

* Client 1
  
  <img width="519" height="448" alt="Screenshot 2026-03-25 194046" src="https://github.com/user-attachments/assets/7bb904ce-b4e0-4cb0-9bd3-f67c84e6b14d" />

* Client 2
  
  <img width="582" height="450" alt="Screenshot 2026-03-25 194106" src="https://github.com/user-attachments/assets/e61b7429-6479-4691-8d27-d7d528cc8805" />

* Client 3
  
  <img width="667" height="315" alt="Screenshot 2026-03-25 194118" src="https://github.com/user-attachments/assets/b8518b0f-4849-4c9e-a381-27b27190cbfb" />

### Server Poll

* Server Side
  
  <img width="346" height="138" alt="Screenshot 2026-03-25 211523" src="https://github.com/user-attachments/assets/7306712b-95df-4188-99e5-b12d856254d8" />

* Client 1
  
  <img width="452" height="232" alt="Screenshot 2026-03-25 210429" src="https://github.com/user-attachments/assets/b1404c29-047b-4d1f-82e8-dab3b55a590f" />

* Client 2
  
  <img width="549" height="233" alt="Screenshot 2026-03-25 210448" src="https://github.com/user-attachments/assets/dd56eea5-5afd-454c-995d-b826555d0163" />

* Client 3
  
  <img width="371" height="381" alt="Screenshot 2026-03-25 210505" src="https://github.com/user-attachments/assets/c1945d1a-572d-4743-9acf-a17fed913998" />

  
# Kesimpulan
* **Sync** cocok untuk sistem sederhana (single client)
* **Thread** cocok untuk multi-client dengan implementasi mudah
* **Select** cocok untuk sistem dengan banyak client dan resource terbatas
* **Poll** cocok untuk sistem dengan banyak koneksi client karena lebih scalable dibanding select dan tidak memiliki batas jumlah file descriptor

Assignment ini menunjukkan perbedaan pendekatan concurrency dalam socket programming, yaitu synchronous, multithreading, dan I/O multiplexing.
