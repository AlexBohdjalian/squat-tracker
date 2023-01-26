import { FlatList, SafeAreaView, ScrollView, Settings, StyleSheet } from 'react-native';
import { Text, View } from '../components/Themed';

const settings = {
  displaySettings: {
    title: 'Display Settings',
    messages: [
      "Video recording settings",
      "Language settings"
    ]
  },
  userPreferencesSettings: {
    title: 'User Settings',
    messages: [
      "Feedback settings",
      "Sound settings",
      "Voice guidance settings",
      "Profile settings",
      "Notifications settings"
    ]
  },
  privacyAndSecuritySettings: {
    title: 'Privacy and Security Settings',
    messages: [
      "Camera settings",
      "Privacy settings",
      "Help and Support settings"
    ]
  }
}

interface SettingsBlockProps {
  settings: {
    title: string;
    messages: string[];
  }
  isFinal?: Boolean,
}

const SettingsBlock = ({ settings }: SettingsBlockProps) => {
  return (
    <SafeAreaView>
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', marginVertical: 10 }}>
        <Text style={styles.title}>{settings.title}</Text>
        <View style={styles.separator} lightColor="#eee" darkColor="rgba(255,255,255,0.1)" />
        <ScrollView>
          <FlatList
            keyExtractor={(item, index) => 'key' + index}
            data={settings.messages}
            renderItem={({ item }) => {
              return (
                <View style={styles.listItem}>
                  <Text style={{ textAlign: 'center' }}>{item}</Text>
                </View>
              );
            }}
          />
        </ScrollView>
        <View style={styles.separator} lightColor="#eee" darkColor="rgba(255,255,255,0.1)" />
      </View>
    </SafeAreaView>
  );
}

export default function VideoScreen() {
  return (
    <ScrollView style={styles.container}>
      <SettingsBlock
        settings={settings.displaySettings}
      />
      <SettingsBlock
        settings={settings.userPreferencesSettings}
      />
      <SettingsBlock
        settings={settings.privacyAndSecuritySettings}
      />
    </ScrollView>
  );
}


const styles = StyleSheet.create({
  container: {
    flex: 1,
    marginHorizontal: 15,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    paddingTop: 30,
  },
  separator: {
    marginVertical: 30,
    height: 1,
    width: '80%',
  },
  listItem: {
    paddingVertical: 5,
  },
  buttonsContainer: {
    marginVertical: 10,
    alignItems: 'center',
  },
});
