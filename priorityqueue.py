import pandas as pd
import folium

class PriorityQueue:
    def __init__(self):
        self.queue = []

    def __str__(self):
        return ' '.join([str(i) for i in self.queue])

    def isEmpty(self):
        return len(self.queue) == 0

    def insert(self, item, priority):
        self.queue.append((priority, item))

    def delete(self):
        try:
            max_val_index = 0
            for i in range(len(self.queue)):
                if self.queue[i][0] > self.queue[max_val_index][0]:
                    max_val_index = i
            item = self.queue[max_val_index]
            del self.queue[max_val_index]
            return item[1]
        except IndexError:
            print("Antrian kosong.")
            exit()

    def display(self):
        return self.queue

class Delivery:
    def __init__(self, name, delivery_option, address, LatCode):
        self.name = name
        self.delivery_option = delivery_option
        self.address = address
        self.LatCode = LatCode

def load_data(file_name):
    try:
        return pd.read_excel(file_name + '.xlsx')
    except FileNotFoundError:
        return None

def save_data(data, file_name):
    data.to_excel(file_name + '_urut.xlsx', index=False)

def delete_top_data(file_name):
    sorted_data = pd.read_excel(file_name + '_urut.xlsx')
    top_data = sorted_data.iloc[0]
    sorted_data = sorted_data.iloc[1:].reset_index(drop=True)
    save_data(sorted_data, file_name)
    return top_data

def create_priority_queue(data):
    pq = PriorityQueue()
    for index, row in data.iterrows():
        name = row['Nama']
        delivery_option = row['Opsi Pengiriman']
        address = row['Alamat']
        LatCode = row['LatCode']

        if delivery_option == 'Instant':
            priority = 4
        elif delivery_option == 'Same Day':
            priority = 3
        elif delivery_option == 'Reguler':
            priority = 2
        elif delivery_option == 'Hemat':
            priority = 1
        else:
            priority = 0

        pq.insert(Delivery(name, delivery_option, address, LatCode), priority)
    return pq

def create_map(data):
    data['LatCode'] = data['LatCode'].str.strip('()')
    latitudes = []
    longitudes = []
    for index, row in data.iterrows():
        lat, lon = row['LatCode'].split(',')
        latitudes.append(float(lat))
        longitudes.append(float(lon))
    data['Latitude'] = latitudes
    data['Longitude'] = longitudes

    sby = folium.Map(location=[-7.305441, 112.7348555], zoom_start=12)
    num = 0
    for index, row in data.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup="Delivery " + row['Nama'],
            icon=folium.Icon(icon=str(num + 1), prefix='fa', color="red")
        ).add_to(sby)
        num += 1

    sby.save("peta.html")

def search_by_name(file_name, name):
    data = pd.read_excel(file_name + '_urut.xlsx')
    result = data[data['Nama'].str.contains(name, case=False, na=False)]
    if not result.empty:
        for idx , row in result.iterrows():
            print(f"{idx + 2}. Nama: {row['Nama']}, Opsi Pengiriman: {row['Opsi Pengiriman']}, Alamat: {row['Alamat']}, LatCode: {row['LatCode']}")
    else:
        print(f"Nama '{name}' tidak ada dalam data.")

def main():
    InputData = ""
    while True:
        print("Menu:")
        print("1. Membaca file, mengurutkan sesuai prioritas, dan membuat file dengan data yang sudah diurutkan")
        print("2. Antrian yang sedang dijalankan")
        print("3. Mencari nama dalam file yang sudah diurutkan")
        print("4. Keluar")
        choice = input("Choose an option (1/2/3/4): ")

        if choice == '1':
            InputData = input("Masukkan nama excel: ")
            data = load_data(InputData)

            if data is None:
                print("File excel tidak ada.")
                continue

            pq = create_priority_queue(data)

            sorted_data = pd.DataFrame(columns=['Nama', 'Opsi Pengiriman', 'Alamat', 'LatCode'])

            while not pq.isEmpty():
                delivery = pq.delete()
                new_row = pd.DataFrame([[delivery.name, delivery.delivery_option, delivery.address, delivery.LatCode]],
                                       columns=['Nama', 'Opsi Pengiriman', 'Alamat', 'LatCode'])
                sorted_data = pd.concat([sorted_data, new_row], ignore_index=True)

            save_data(sorted_data, InputData)
            print(f"File '{InputData}_urut.xlsx' berhasil dibuat.")

        elif choice == '2':
            InputData = input("Masukkan nama excel (sorted file): ")

            try:
                top_data = pd.read_excel(InputData + '_urut.xlsx').iloc[0]
                print("Antrian yang sedang dijalankan:")
                print(f"Nama: {top_data['Nama']}, Opsi Pengiriman: {top_data['Opsi Pengiriman']}, Alamat: {top_data['Alamat']}, LatCode: {top_data['LatCode']}")
                response = input("Apakah paket sudah dikirim? (sudah/belum): ").strip().lower()

                if response == 'sudah':
                    delete_top_data(InputData)
                    print("Data tersebut berhasil dihapus.")
                else:
                    print("Segera kirimkan paket tersebut.")
            except FileNotFoundError:
                print("File excel tidak ada.")
            except IndexError:
                print("Data kosong.")

        elif choice == '3':
            InputData = input("Masukkan nama excel (sorted file): ")
            try:
                name = input("Masukkan nama yang ingin dicari: ")
                search_by_name(InputData, name)
            except FileNotFoundError:
                print("File excel tidak ada.")

        elif choice == '4':
            print("Keluar dari aplikasi.")
            break

        else:
            print("Pilihan salah, silahkan pilih ulang.")

    if choice == '4' and InputData:
        updated_sorted_data = pd.read_excel(InputData + '_urut.xlsx')
        create_map(updated_sorted_data)
        print("Peta terupdate dan di save sebagai 'peta.html'.")

if __name__ == "__main__":
    main()
