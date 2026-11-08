//+------------------------------------------------------------------+
//| ExportDataBacktest.mq5                                           |
//| Mengekspor data candle (M5 dan H1) ke file CSV untuk backtest.   |
//| Script ini HANYA membaca data harga. Tidak membuka/menutup order. |
//| Hasil: folder MQL5\Files (File -> Open Data Folder -> MQL5\Files) |
//+------------------------------------------------------------------+
#property copyright "jurnal-trading"
#property version   "1.00"
#property script_show_inputs

input string   InpSymbols = "GBPUSD,USDJPY";       // Simbol, pisahkan dengan koma
input datetime InpFrom    = D'2016.01.01 00:00';   // Ambil data mulai tanggal ini
input bool     InpM5      = true;                  // Ekspor M5
input bool     InpH1      = true;                  // Ekspor H1

//--- ambil data dengan beberapa kali percobaan (terminal kadang masih mengunduh history)
int GetRates(const string sym, const ENUM_TIMEFRAMES tf, MqlRates &r[])
  {
   ArraySetAsSeries(r, false);
   int n = -1;
   for(int attempt = 0; attempt < 10 && !IsStopped(); attempt++)
     {
      ResetLastError();
      n = CopyRates(sym, tf, InpFrom, TimeCurrent(), r);
      if(n > 0 && SeriesInfoInteger(sym, tf, SERIES_SYNCHRONIZED))
         break;
      Sleep(1500);
     }
   return n;
  }

void ExportTF(const string sym, const ENUM_TIMEFRAMES tf, const string tfname)
  {
   MqlRates r[];
   int n = GetRates(sym, tf, r);
   if(n <= 0)
     {
      PrintFormat("%s %s: gagal mengambil data (error %d)", sym, tfname, GetLastError());
      return;
     }
   string fn = sym + "_" + tfname + ".csv";
   int h = FileOpen(fn, FILE_WRITE | FILE_TXT | FILE_ANSI);
   if(h == INVALID_HANDLE)
     {
      PrintFormat("Gagal membuat file %s (error %d)", fn, GetLastError());
      return;
     }
   int dg = (int)SymbolInfoInteger(sym, SYMBOL_DIGITS);
   FileWriteString(h, "time,open,high,low,close,tick_volume,spread\r\n");
   for(int i = 0; i < n; i++)
     {
      string line = TimeToString(r[i].time, TIME_DATE | TIME_MINUTES) + "," +
                    DoubleToString(r[i].open, dg) + "," +
                    DoubleToString(r[i].high, dg) + "," +
                    DoubleToString(r[i].low, dg) + "," +
                    DoubleToString(r[i].close, dg) + "," +
                    IntegerToString(r[i].tick_volume) + "," +
                    IntegerToString(r[i].spread) + "\r\n";
      FileWriteString(h, line);
     }
   FileClose(h);
   PrintFormat("%s: %d candle, %s s/d %s", fn, n,
               TimeToString(r[0].time), TimeToString(r[n - 1].time));
  }

void OnStart()
  {
   string syms[];
   int k = StringSplit(InpSymbols, ',', syms);
   for(int i = 0; i < k && !IsStopped(); i++)
     {
      string s = syms[i];
      StringTrimLeft(s);
      StringTrimRight(s);
      if(s == "")
         continue;
      if(!SymbolSelect(s, true))
        {
         PrintFormat("Simbol %s tidak ditemukan di broker ini", s);
         continue;
        }
      if(InpM5)
         ExportTF(s, PERIOD_M5, "M5");
      if(InpH1)
         ExportTF(s, PERIOD_H1, "H1");
     }
   //--- catat zona waktu server broker
   int offset_h = (int)MathRound((double)(TimeTradeServer() - TimeGMT()) / 3600.0);
   int h = FileOpen("info_server.txt", FILE_WRITE | FILE_TXT | FILE_ANSI);
   if(h != INVALID_HANDLE)
     {
      FileWriteString(h, "server=" + AccountInfoString(ACCOUNT_SERVER) + "\r\n");
      FileWriteString(h, "gmt_offset_jam=" + IntegerToString(offset_h) + "\r\n");
      FileWriteString(h, "waktu_server=" + TimeToString(TimeTradeServer(), TIME_DATE | TIME_SECONDS) + "\r\n");
      FileWriteString(h, "waktu_gmt=" + TimeToString(TimeGMT(), TIME_DATE | TIME_SECONDS) + "\r\n");
      FileClose(h);
     }
   Alert("Ekspor selesai. Buka File -> Open Data Folder -> MQL5 -> Files. Detail ada di tab Experts.");
  }
//+------------------------------------------------------------------+
