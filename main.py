from scripts import ensembl, cosmic, mirgene, orthologs, enhanceratlas, liftover, cosmic_env, rna_files, gaps_ftp, wget
from utils.logger import write_logs_to_disk

def menu():
    while True:
        print("\n==== Choose from the Menu ====")
        print("1. Download Ensembl data")
        print("2. Download miRGene data")
        print("3. Download Orthologs data")
        print("4. Download COSMIC data")
        print("5. Download EnhancerAtlas (retain dr.bed)")
        print("6. Run Liftover on dr.bed file")
        print("7. Download lncRNA and tRNA files")
        print("8. USCS_Gaps_FTP")
        print("9. WGET")
        #print("0. cosmic env")
        print("10. Exit")

        choice = input("Enter your choice: ").strip()
        if choice == '1': ensembl.download()
        elif choice == '2': mirgene.download()
        elif choice == '3': orthologs.download()
        elif choice == '4': cosmic.download()
        elif choice == '5': enhanceratlas.download()
        elif choice == '6': liftover.run()
        elif choice == '7': rna_files.main()
        elif choice == '8': gaps_ftp.download_ucsc_gap_data()
        elif choice == '9': wget.download_chrominfo()
        # elif choice == '0': cosmic_env.download_cosmic_file()
        elif choice == '10': 
            # write_logs_to_disk()
            print("Exiting. Arigatooo User"); break
        else: print("Invalid option.")

if __name__ == "__main__":
    menu()
