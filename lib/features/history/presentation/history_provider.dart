import 'package:flutter/foundation.dart';
import '../data/dummy_history_repository.dart';
import '../../inbox/domain/sms_message.dart';

/// Manages state for the History screen, including loading, filtering,
/// searching, and sorting of previously analyzed SMS messages.
class HistoryProvider extends ChangeNotifier {
  HistoryProvider() {
    loadHistory();
  }

  final _repo = DummyHistoryRepository.instance;

  // ── Internal state ────────────────────────────────────────────────────────

  List<SmsMessage> _allMessages = [];
  bool _isLoading = false;
  String? _errorMessage;

  // Filter & Sort State
  AiStatus? _filterStatus;
  String _searchQuery = '';
  bool _isSortAscending = false;

  // ── Public getters ────────────────────────────────────────────────────────

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  AiStatus? get filterStatus => _filterStatus;
  String get searchQuery => _searchQuery;
  bool get isSortAscending => _isSortAscending;

  /// Returns the messages after applying search, filter, and sorting.
  List<SmsMessage> get filteredMessages {
    var result = _allMessages.where((msg) {
      // 1. Apply status filter
      if (_filterStatus != null && msg.aiStatus != _filterStatus) {
        return false;
      }

      // 2. Apply search query
      if (_searchQuery.isNotEmpty) {
        final query = _searchQuery.toLowerCase();
        final matchesSender = msg.sender.toLowerCase().contains(query);
        final matchesBody = msg.body.toLowerCase().contains(query);
        if (!matchesSender && !matchesBody) {
          return false;
        }
      }

      return true;
    }).toList();

    // 3. Apply sorting by date
    result.sort((a, b) {
      if (_isSortAscending) {
        return a.timestamp.compareTo(b.timestamp);
      } else {
        return b.timestamp.compareTo(a.timestamp);
      }
    });

    return result;
  }

  // ── Public API ────────────────────────────────────────────────────────────

  Future<void> loadHistory() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _allMessages = await _repo.fetchHistory();
    } catch (e, st) {
      _errorMessage = 'Failed to load history: $e';
      debugPrintStack(stackTrace: st);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void setFilter(AiStatus? status) {
    _filterStatus = status;
    notifyListeners();
  }

  void setSearchQuery(String query) {
    _searchQuery = query;
    notifyListeners();
  }

  void toggleSort() {
    _isSortAscending = !_isSortAscending;
    notifyListeners();
  }
}
